from nidan.lims.auth import require_tenant
from nidan.lims.roles import has_permission


class PermissionError(ValueError):
    """Raised when a user lacks a required NIDAN permission."""


def require_permission(user, tenant_id, permission):
    """Require tenant membership and the exact role permission."""
    require_tenant(user, tenant_id)
    role = user.get("role")
    if not has_permission(role, permission):
        raise PermissionError(
            "Role %s lacks permission %s" % (role, permission)
        )
    return True
