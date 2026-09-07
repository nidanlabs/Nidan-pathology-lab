from datetime import date, timedelta
import unittest

from nidan.lims.tenant import (
    TenantError,
    build_tenant,
    get_plan_limits,
    subscription_is_active,
    within_limit,
)


class TestTenant(unittest.TestCase):
    def test_build_tenant(self):
        tenant = build_tenant("LAB-001", "Nidan Demo Lab", "owner@example.com")
        self.assertEqual("trial", tenant["status"])
        self.assertEqual("starter", tenant["plan"])

    def test_invalid_plan(self):
        with self.assertRaises(TenantError):
            build_tenant("LAB-001", "Demo", "owner@example.com", plan="unknown")

    def test_plan_limits(self):
        limits = get_plan_limits("professional")
        self.assertEqual(10, limits["users"])
        self.assertEqual(3, limits["branches"])

    def test_suspended_tenant_is_inactive(self):
        tenant = build_tenant("LAB-001", "Demo", "owner@example.com", status="suspended")
        self.assertFalse(subscription_is_active(tenant))

    def test_expired_subscription(self):
        tenant = build_tenant("LAB-001", "Demo", "owner@example.com", status="active")
        tenant["subscription_expires"] = date.today() - timedelta(days=1)
        self.assertFalse(subscription_is_active(tenant))

    def test_usage_limit(self):
        self.assertTrue(within_limit("starter", "users", 2))
        self.assertFalse(within_limit("starter", "users", 3))


if __name__ == "__main__":
    unittest.main()
