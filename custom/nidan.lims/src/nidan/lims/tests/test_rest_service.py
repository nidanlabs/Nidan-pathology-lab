import pytest

from nidan.lims.auth import build_user
from nidan.lims.rest_service import RESTServiceError, patient_resource, report_resource


def test_patient_resource_is_tenant_scoped():
    user = build_user("U1", "LAB-1", "owner@example.com", role="owner")
    resource = patient_resource(user, "LAB-1", {
        "id": "P1",
        "tenant_id": "LAB-1",
        "patient_id": "P1",
        "first_name": "Ravi",
        "last_name": "Kumar",
        "sex": "M",
    })
    assert resource["type"] == "nidan.patient"
    assert resource["tenant_id"] == "LAB-1"


def test_cross_tenant_resource_is_rejected():
    user = build_user("U1", "LAB-1", "owner@example.com", role="owner")
    with pytest.raises(Exception):
        patient_resource(user, "LAB-1", {"id": "P1", "tenant_id": "LAB-2", "patient_id": "P1"})


def test_report_resource_exposes_only_declared_fields():
    user = build_user("U1", "LAB-1", "pathologist@example.com", role="pathologist")
    resource = report_resource(user, "LAB-1", {
        "id": "R1",
        "tenant_id": "LAB-1",
        "report_id": "R1",
        "patient": {"patient_id": "P1"},
        "sample": {"sample_id": "S1"},
        "results": [],
        "state": "released",
        "secret": "must-not-leak",
    })
    assert "secret" not in resource
    assert resource["state"] == "released"
