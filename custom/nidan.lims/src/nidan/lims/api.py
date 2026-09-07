"""Core domain helpers for NIDAN LIMS.

The API is intentionally framework-light so domain validation can be tested
independently from Plone/SENAITE integration code.
"""

from datetime import date


REQUIRED_PATIENT_FIELDS = ("patient_id", "first_name", "last_name", "date_of_birth", "sex")


def validate_patient(data):
    """Validate the minimum patient registration payload.

    Returns a list of human-readable validation errors.
    """
    errors = []
    for field in REQUIRED_PATIENT_FIELDS:
        if not data.get(field):
            errors.append("%s is required" % field)

    dob = data.get("date_of_birth")
    if dob and not isinstance(dob, date):
        errors.append("date_of_birth must be a date")

    sex = data.get("sex")
    if sex and sex not in ("M", "F", "O"):
        errors.append("sex must be M, F or O")

    return errors


def build_accession_number(sequence, year=None):
    """Build a human-readable NIDAN accession number."""
    year = year or date.today().year
    return "NIDAN-%04d-%06d" % (year, int(sequence))
