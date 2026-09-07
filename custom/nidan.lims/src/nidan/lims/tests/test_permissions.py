import pytest

from nidan.lims.auth import build_user
from nidan.lims.permissions import PermissionError, require_permission


def test_receptionist_can_manage_patients_and_samples():
    user = build_user("U1", "LAB-1", "frontdesk@example.com", role="receptionist")
    assert require_permission(user, "LAB-1", "manage_patients") is True
    assert require_permission(user, "LAB-1", "manage_samples") is True


def test_technician_cannot_manage_patients():
    user = build_user("U2", "LAB-1", "tech@example.com", role="technician")
    with pytest.raises(PermissionError):
        require_permission(user, "LAB-1", "manage_patients")


def test_cross_tenant_permission_is_denied():
    user = build_user("U3", "LAB-1", "owner@example.com", role="owner")
    with pytest.raises(Exception):
        require_permission(user, "LAB-2", "manage_patients")
