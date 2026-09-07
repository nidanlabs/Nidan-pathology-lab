"""Patient and referring-doctor management helpers for NIDAN."""


SEX_VALUES = ("M", "F", "O")
DOCTOR_STATUSES = ("active", "inactive")


def validate_patient_record(data):
    """Validate patient registration data."""
    errors = []
    required = ("patient_id", "first_name", "last_name", "sex")
    for field in required:
        if not data.get(field):
            errors.append("%s is required" % field)
    if data.get("sex") and data.get("sex") not in SEX_VALUES:
        errors.append("sex must be M, F or O")
    return errors


def validate_doctor(data):
    """Validate referring-doctor data."""
    errors = []
    for field in ("doctor_id", "name"):
        if not data.get(field):
            errors.append("%s is required" % field)
    status = data.get("status", "active")
    if status not in DOCTOR_STATUSES:
        errors.append("status must be active or inactive")
    return errors


def build_doctor(data):
    errors = validate_doctor(data)
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "doctor_id": data["doctor_id"],
        "name": data["name"],
        "qualification": data.get("qualification", ""),
        "specialty": data.get("specialty", ""),
        "phone": data.get("phone", ""),
        "clinic": data.get("clinic", ""),
        "status": data.get("status", "active"),
    }


def build_patient_record(data, referring_doctor_id=None):
    errors = validate_patient_record(data)
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "patient_id": data["patient_id"],
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "date_of_birth": data.get("date_of_birth"),
        "sex": data["sex"],
        "phone": data.get("phone", ""),
        "address": data.get("address", ""),
        "referring_doctor_id": referring_doctor_id or data.get("referring_doctor_id"),
    }
