"""Commercial multi-tenant foundation for NIDAN SaaS.

This module deliberately keeps tenant rules independent from Plone/Zope APIs so
that the rules can be tested and later bound to SENAITE objects, users, and
persistent storage.
"""

from datetime import date


PLAN_LIMITS = {
    "starter": {"users": 3, "branches": 1, "monthly_reports": 500},
    "professional": {"users": 10, "branches": 3, "monthly_reports": 3000},
    "premium": {"users": 50, "branches": 10, "monthly_reports": 15000},
}

TENANT_STATUSES = ("trial", "active", "past_due", "suspended", "cancelled")


class TenantError(ValueError):
    """Raised when tenant data or subscription rules are invalid."""


def validate_tenant(data):
    """Validate the minimum commercial tenant record."""
    required = ("tenant_id", "name", "owner_email", "status", "plan")
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise TenantError("Missing required tenant fields: %s" % ", ".join(missing))
    if data["status"] not in TENANT_STATUSES:
        raise TenantError("Invalid tenant status: %s" % data["status"])
    if data["plan"] not in PLAN_LIMITS:
        raise TenantError("Unknown plan: %s" % data["plan"])
    return True


def build_tenant(tenant_id, name, owner_email, plan="starter", status="trial"):
    """Create a normalized tenant record."""
    tenant = {
        "tenant_id": tenant_id,
        "name": name,
        "owner_email": owner_email,
        "plan": plan,
        "status": status,
    }
    validate_tenant(tenant)
    return tenant


def get_plan_limits(plan):
    """Return a copy of the limits for a commercial plan."""
    if plan not in PLAN_LIMITS:
        raise TenantError("Unknown plan: %s" % plan)
    return dict(PLAN_LIMITS[plan])


def subscription_is_active(tenant, today=None):
    """Return whether the tenant can currently use the application."""
    validate_tenant(tenant)
    if tenant["status"] in ("suspended", "cancelled"):
        return False
    expiry = tenant.get("subscription_expires")
    if expiry is None:
        return True
    if isinstance(expiry, date):
        return expiry >= (today or date.today())
    raise TenantError("subscription_expires must be a date")


def within_limit(plan, resource, current_count):
    """Check a usage count against the selected plan's commercial limit."""
    limits = get_plan_limits(plan)
    if resource not in limits:
        raise TenantError("Unknown resource: %s" % resource)
    return current_count < limits[resource]
