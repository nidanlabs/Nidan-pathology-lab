import unittest
from datetime import date

from nidan.lims.auth import AuthError, build_user
from nidan.lims.end_to_end import (
    EndToEndWorkflowError,
    complete_order_with_report,
    create_order_with_billing,
)


class TestEndToEndWorkflow(unittest.TestCase):
    def setUp(self):
        self.user = build_user("USR-1", "LAB-1", "owner@nidan.test", role="owner")
        self.patient = {
            "patient_id": "P-001",
            "first_name": "Demo",
            "last_name": "Patient",
            "date_of_birth": date(1990, 1, 1),
            "sex": "M",
        }
        self.sample = {
            "sample_id": "S-001",
            "patient_id": "P-001",
            "sample_type": "EDTA",
        }
        self.items = [
            {"code": "CBC", "name": "Complete Blood Count", "quantity": 1, "unit_price": "250"},
        ]

    def test_full_patient_to_report_release(self):
        context = create_order_with_billing(
            self.user, "LAB-1", self.patient, self.sample, ["CBC"], self.items, paid="100"
        )
        results = [{
            "state": "verified",
            "test_code": "CBC",
            "test_name": "Complete Blood Count",
            "parameters": [{"code": "HB", "value": "13.2", "unit": "g/dL"}],
        }]
        completed = complete_order_with_report(
            self.user, "LAB-1", context, results, "R-001", remarks="Routine report"
        )
        self.assertEqual("report_released", completed["order"]["status"])
        self.assertEqual("released", completed["report"]["state"])
        self.assertEqual(24, len(completed["report"]["verification_token"]))

    def test_cross_tenant_context_denied(self):
        context = create_order_with_billing(
            self.user, "LAB-1", self.patient, self.sample, ["CBC"], self.items
        )
        with self.assertRaises(AuthError):
            complete_order_with_report(self.user, "LAB-2", context, [], "R-002")

    def test_unverified_results_denied(self):
        context = create_order_with_billing(
            self.user, "LAB-1", self.patient, self.sample, ["CBC"], self.items
        )
        results = [{"state": "entered", "test_code": "CBC", "parameters": []}]
        with self.assertRaises(EndToEndWorkflowError):
            complete_order_with_report(self.user, "LAB-1", context, results, "R-003")


if __name__ == "__main__":
    unittest.main()
