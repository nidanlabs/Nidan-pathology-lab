"""Authentication and tenant-isolation primitives for NIDAN SaaS.

The functions here define application-level rules. Production credential
storage/authentication must be delegated to a proven identity system such as
Plone PAS or another audited identity provider; passwords are never stored by
this module.
"""


class AuthError(ValueError):
    """Raised for invalid authentication or tenant access."""


def build_user(user_id, tenant_id, email, role="receptionist", active=True):
    """Create a normalized application user record without credentials."""
    if not user_id or not tenant_id or not email:
        raise AuthError("user_id, tenant_id and email are required")
    if not isinstance(active, bool):
        raise AuthError("active must be boolean")
    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "email": email,
        "role": role,
        "active": active,
    }


def authorize_tenant(user, tenant_id):
    """Allow access only when an active user belongs to the requested tenant."""
    if not user or not user.get("active"):
        return False
    return user.get("tenant_id") == tenant_id


def require_tenant(user, tenant_id):
    """Raise instead of silently allowing a cross-tenant operation."""
    if not authorize_tenant(user, tenant_id):
        raise AuthError("User is not authorized for this tenant")
    return True


def scope_record(record, tenant_id):
    """Stamp a domain record with its owning tenant."""
    if not tenant_id:
        raise AuthError("tenant_id is required")
    scoped = dict(record)
    scoped["tenant_id"] = tenant_id
    return scoped
