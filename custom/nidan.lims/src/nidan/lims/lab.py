"""Lab registration and settings model for NIDAN SaaS."""

from nidan.lims.tenant import build_tenant


class LabError(ValueError):
    """Raised when a lab registration is invalid."""


def register_lab(lab_id, name, owner_email, phone=None, address=None, plan="starter"):
    """Create the initial tenant/lab account record."""
    if not phone:
        raise LabError("phone is required for lab registration")
    lab = build_tenant(lab_id, name, owner_email, plan=plan, status="trial")
    lab.update({
        "phone": phone,
        "address": address or "",
        "logo_url": "",
        "letterhead_enabled": True,
        "timezone": "Asia/Kolkata",
        "currency": "INR",
    })
    return lab


def update_lab_settings(lab, **settings):
    """Update whitelisted presentation/operational lab settings."""
    allowed = (
        "name", "phone", "address", "logo_url", "letterhead_enabled",
        "timezone", "currency",
    )
    updated = dict(lab)
    for key, value in settings.items():
        if key not in allowed:
            raise LabError("Setting cannot be changed here: %s" % key)
        updated[key] = value
    return updated
