"""NIDAN application roles and permission model."""


ROLES = {
    "owner": (
        "manage_lab",
        "manage_users",
        "manage_billing",
        "manage_tests",
        "manage_patients",
        "manage_samples",
        "enter_results",
        "verify_results",
        "release_reports",
        "view_reports",
    ),
    "admin": (
        "manage_users",
        "manage_tests",
        "manage_patients",
        "manage_samples",
        "enter_results",
        "verify_results",
        "release_reports",
        "view_reports",
    ),
    "technician": (
        "enter_results",
        "view_reports",
    ),
    "pathologist": (
        "verify_results",
        "release_reports",
        "view_reports",
    ),
    "receptionist": (
        "view_reports",
        "manage_patients",
        "manage_samples",
    ),
}


def has_permission(role, permission):
    """Return whether a NIDAN role has the requested permission."""
    if role not in ROLES:
        return False
    return permission in ROLES[role]
