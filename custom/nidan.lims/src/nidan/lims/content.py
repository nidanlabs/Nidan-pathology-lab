"""Plone/SENAITE-facing content specifications for NIDAN.

These declarative specifications mirror the Dexterity field contracts and
keep tenant ownership explicit for every persistent record.
"""


CONTENT_TYPES = {
    "NIDANPatient": {
        "portal_type": "NIDAN Patient",
        "fields": (
            "tenant_id", "patient_id", "first_name", "last_name", "date_of_birth",
            "sex", "phone", "address", "referring_doctor_id",
        ),
    },
    "NIDANSample": {
        "portal_type": "NIDAN Sample",
        "fields": (
            "tenant_id", "sample_id", "patient_id", "sample_type", "status",
            "collection_date",
        ),
    },
    "NIDANReport": {
        "portal_type": "NIDAN Report",
        "fields": (
            "tenant_id", "report_id", "patient_id", "sample_id", "state",
            "remarks",
        ),
    },
}


def get_content_type(name):
    """Return a content specification or None for an unknown type."""
    return CONTENT_TYPES.get(name)


def list_content_types():
    """Return content type names in deterministic order."""
    return sorted(CONTENT_TYPES.keys())
