import unittest
from datetime import date

from nidan.lims.auth import AuthError, build_user
from nidan.lims.permissions import PermissionError
from nidan.lims.workflow import WorkflowError, create_test_order, register_patient


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.user = build_user("USR-001", "LAB-001", "staff@example.com", role="owner")
        self.technician = build_user("USR-002", "LAB-001", "tech@example.com", role="technician")
        self.patient = {
            "patient_id": "P-001",
            "first_name": "Demo",
            "last_name": "Patient",
            "date_of_birth": date(1990, 1, 1),
            "sex": "M",
        }

    def test_patient_is_tenant_scoped(self):
        result = register_patient(self.user, "LAB-001", self.patient)
        self.assertEqual("LAB-001", result["tenant_id"])

    def test_cross_tenant_patient_is_denied(self):
        with self.assertRaises(AuthError):
            register_patient(self.user, "LAB-002", self.patient)

    def test_technician_cannot_register_patient(self):
        with self.assertRaises(PermissionError):
            register_patient(self.technician, "LAB-001", self.patient)

    def test_test_order_is_tenant_scoped(self):
        order = create_test_order(self.user, "LAB-001", "P-001", "S-001", ["CBC", "LFT"])
        self.assertEqual("LAB-001", order["tenant_id"])
        self.assertEqual("ordered", order["status"])

    def test_duplicate_test_ids_are_rejected(self):
        with self.assertRaises(WorkflowError):
            create_test_order(self.user, "LAB-001", "P-001", "S-001", ["CBC", "CBC"])

    def test_test_order_requires_tests(self):
        with self.assertRaises(WorkflowError):
            create_test_order(self.user, "LAB-001", "P-001", "S-001", [])


if __name__ == "__main__":
    unittest.main()
