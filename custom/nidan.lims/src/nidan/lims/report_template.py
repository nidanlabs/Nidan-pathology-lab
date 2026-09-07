"""Lab-configurable report presentation contract."""


class ReportTemplateError(ValueError):
    """Raised for invalid report template settings."""


DEFAULT_TEMPLATE = {
    "name": "NIDAN Standard",
    "show_logo": True,
    "show_lab_address": True,
    "show_patient_details": True,
    "show_sample_details": True,
    "show_reference_ranges": True,
    "show_remarks": True,
    "show_qr_verification": True,
    "show_pathologist_signature": True,
}


def build_template(tenant_id, name=None, **settings):
    """Create a tenant-owned report template configuration."""
    if not tenant_id:
        raise ReportTemplateError("tenant_id is required")
    template = dict(DEFAULT_TEMPLATE)
    template["tenant_id"] = tenant_id
    if name:
        template["name"] = name
    for key, value in settings.items():
        if key not in DEFAULT_TEMPLATE:
            raise ReportTemplateError("Unknown template setting: %s" % key)
        if not isinstance(value, bool):
            raise ReportTemplateError("Template setting must be boolean: %s" % key)
        template[key] = value
    return template
