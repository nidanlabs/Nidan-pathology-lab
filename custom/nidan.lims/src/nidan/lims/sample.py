"""Sample accession domain logic."""

from datetime import date


SAMPLE_TYPES = {
    "EDTA": "EDTA Whole Blood",
    "SERUM": "Serum",
    "PLASMA": "Plasma",
    "URINE": "Urine",
    "STOOL": "Stool",
    "SWAB": "Swab",
    "FLUID": "Body Fluid",
}


STATUSES = ("registered", "collected", "received", "processing", "completed", "rejected")


def validate_sample(data):
    """Validate a sample registration payload."""
    errors = []
    for field in ("sample_id", "patient_id", "sample_type"):
        if not data.get(field):
            errors.append("%s is required" % field)

    sample_type = data.get("sample_type")
    if sample_type and sample_type not in SAMPLE_TYPES:
        errors.append("sample_type is invalid")

    status = data.get("status", "registered")
    if status not in STATUSES:
        errors.append("status is invalid")

    collection_date = data.get("collection_date")
    if collection_date and not isinstance(collection_date, date):
        errors.append("collection_date must be a date")

    return errors


def next_sample_status(current, target):
    """Return whether a sample status transition is allowed."""
    transitions = {
        "registered": {"collected", "rejected"},
        "collected": {"received", "rejected"},
        "received": {"processing", "rejected"},
        "processing": {"completed", "rejected"},
        "completed": set(),
        "rejected": set(),
    }
    if target not in transitions.get(current, set()):
        raise ValueError("Invalid sample status transition: %s -> %s" % (current, target))
    return target
