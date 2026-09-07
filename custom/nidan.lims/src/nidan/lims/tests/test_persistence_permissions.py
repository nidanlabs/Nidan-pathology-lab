import unittest

from nidan.lims.auth import AuthError, build_user
from nidan.lims.persistence import PersistenceError, TenantRepository
from nidan.lims.permissions import PermissionError, require_permission


class TestPersistenceAndPermissions(unittest.TestCase):
    def setUp(self):
        self.owner = build_user("U1", "LAB-1", "owner@test", role="owner")
        self.tech = build_user("U2", "LAB-1", "tech@test", role="technician")
        self.foreign = build_user("U3", "LAB-2", "other@test", role="owner")
        self.repo = TenantRepository()

    def test_save_and_get_is_tenant_scoped(self):
        record = {"tenant_id": "LAB-1", "patient_id": "P1", "first_name": "A"}
        self.repo.save(self.owner, "LAB-1", "patient", "P1", record)
        self.assertEqual("P1", self.repo.get(self.owner, "LAB-1", "patient", "P1")["patient_id"])
        with self.assertRaises(PersistenceError):
            self.repo.get(self.owner, "LAB-1", "patient", "missing")

    def test_foreign_tenant_denied(self):
        record = {"tenant_id": "LAB-1", "patient_id": "P1"}
        with self.assertRaises(PersistenceError):
            self.repo.save(self.foreign, "LAB-1", "patient", "P1", record)
        with self.assertRaises(AuthError):
            self.repo.get(self.foreign, "LAB-1", "patient", "P1")

    def test_permission_matrix(self):
        self.assertTrue(require_permission(self.owner, "LAB-1", "manage_users"))
        self.assertTrue(require_permission(self.tech, "LAB-1", "enter_results"))
        with self.assertRaises(PermissionError):
            require_permission(self.tech, "LAB-1", "release_reports")


if __name__ == "__main__":
    unittest.main()
