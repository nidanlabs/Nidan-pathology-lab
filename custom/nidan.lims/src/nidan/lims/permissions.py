"""Application-level permission checks for NIDAN workflows."""

from nidan.lims.auth import require_tenant
from nidan.lims.roles import has_permission


class PermissionError(ValueError):
    """Raised when a user lacks a required NIDAN permission."""


def require_permission(user, tenant_id, permission):
    require_tenant(user, tenant_id)
    if not has_permission(user.get("role"), permission):
        raise PermissionError("permission denied: %s" % permission)
    return True
