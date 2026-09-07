import unittest
from datetime import date

from nidan.lims.auth import AuthError, build_user
from nidan.lims.senaite_integration import (
    SENAITEIntegrationError,
    build_senaite_bundle,
)


class TestSENAITEIntegration(unittest.TestCase):
    def setUp(self):
        self.user = build_user("USR-1", "LAB-1", "owner@nidan.test", role="owner")
        self.patient = {
            "tenant_id": "LAB-1", "patient_id": "P-001", "first_name": "Demo",
            "last_name": "Patient", "date_of_birth": date(1990, 1, 1), "sex": "M",
        }
        self.sample = {
            "tenant_id": "LAB-1", "sample_id": "S-001", "patient_id": "P-001",
            "sample_type": "EDTA", "status": "registered",
        }
        self.order = {
            "tenant_id": "LAB-1", "patient_id": "P-001", "sample_id": "S-001",
            "test_ids": ["CBC"], "status": "ordered",
        }
        self.report = {
            "tenant_id": "LAB-1", "report_id": "R-001", "patient_id": "P-001",
            "sample_id": "S-001", "state": "released", "results": [],
        }

    def test_bundle_is_tenant_scoped(self):
        bundle = build_senaite_bundle(
            self.user, "LAB-1", self.patient, self.sample, self.order, self.report
        )
        self.assertEqual("LAB-1", bundle["tenant_id"])
        self.assertEqual("P-001", bundle["patient"]["patient_id"])
        self.assertEqual("S-001", bundle["sample"]["sample_id"])

    def test_cross_tenant_user_denied(self):
        with self.assertRaises(AuthError):
            build_senaite_bundle(
                self.user, "LAB-2", self.patient, self.sample, self.order, self.report
            )

    def test_cross_tenant_record_denied(self):
        foreign_report = dict(self.report, tenant_id="LAB-2")
        with self.assertRaises(SENAITEIntegrationError):
            build_senaite_bundle(
                self.user, "LAB-1", self.patient, self.sample, self.order, foreign_report
            )


if __name__ == "__main__":
    unittest.main()
