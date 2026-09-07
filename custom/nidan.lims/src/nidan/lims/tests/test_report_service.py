import unittest

from nidan.lims.auth import build_user
from nidan.lims.report_service import (
    ReportServiceError,
    build_verification_token,
    public_verification_payload,
    release_tenant_report,
)
from nidan.lims.report_template import ReportTemplateError, build_template


class TestReportService(unittest.TestCase):
    def setUp(self):
        self.user = build_user("USR-1", "LAB-1", "staff@example.com", role="pathologist")
        self.report = {
            "tenant_id": "LAB-1",
            "report_id": "R-001",
            "patient_id": "P-001",
            "sample_id": "S-001",
            "state": "verified",
            "results": [{"state": "verified"}],
        }

    def test_release_same_tenant(self):
        released = release_tenant_report(self.user, "LAB-1", self.report)
        self.assertEqual("released", released["state"])

    def test_cross_tenant_release_denied(self):
        with self.assertRaises(ReportServiceError):
            release_tenant_report(self.user, "LAB-2", self.report)

    def test_verification_token_is_stable(self):
        first = build_verification_token("LAB-1", "R-001")
        second = build_verification_token("LAB-1", "R-001")
        self.assertEqual(first, second)
        self.assertEqual(24, len(first))

    def test_public_payload_is_minimal(self):
        payload = public_verification_payload(self.report)
        self.assertNotIn("results", payload)
        self.assertEqual("R-001", payload["report_id"])

    def test_template(self):
        template = build_template("LAB-1", show_qr_verification=False)
        self.assertFalse(template["show_qr_verification"])
        self.assertEqual("LAB-1", template["tenant_id"])

    def test_invalid_template_setting(self):
        with self.assertRaises(ReportTemplateError):
            build_template("LAB-1", unknown=True)


if __name__ == "__main__":
    unittest.main()
