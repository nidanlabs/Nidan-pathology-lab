import unittest

from nidan.lims.auth import (
    AuthError,
    authorize_tenant,
    build_user,
    require_tenant,
    scope_record,
)


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.user = build_user(
            "USR-001", "LAB-001", "staff@example.com", role="technician"
        )

    def test_user_contains_tenant(self):
        self.assertEqual("LAB-001", self.user["tenant_id"])
        self.assertEqual("technician", self.user["role"])

    def test_same_tenant_is_authorized(self):
        self.assertTrue(authorize_tenant(self.user, "LAB-001"))

    def test_cross_tenant_is_denied(self):
        self.assertFalse(authorize_tenant(self.user, "LAB-002"))
        with self.assertRaises(AuthError):
            require_tenant(self.user, "LAB-002")

    def test_inactive_user_is_denied(self):
        inactive = build_user("USR-002", "LAB-001", "x@example.com", active=False)
        self.assertFalse(authorize_tenant(inactive, "LAB-001"))

    def test_scope_record(self):
        record = scope_record({"patient_id": "P-001"}, "LAB-001")
        self.assertEqual("LAB-001", record["tenant_id"])


if __name__ == "__main__":
    unittest.main()
