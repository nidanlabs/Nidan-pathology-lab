from datetime import date

from nidan.lims.api import build_accession_number, validate_patient


def test_build_accession_number():
    assert build_accession_number(42, 2026) == "NIDAN-2026-000042"


def test_validate_patient_accepts_valid_payload():
    patient = {
        "patient_id": "P0001",
        "first_name": "Ravi",
        "last_name": "Kumar",
        "date_of_birth": date(1990, 1, 1),
        "sex": "M",
    }
    assert validate_patient(patient) == []


def test_validate_patient_reports_missing_fields():
    errors = validate_patient({})
    assert "patient_id is required" in errors
    assert "first_name is required" in errors
    assert "date_of_birth is required" in errors


def test_validate_patient_rejects_invalid_sex():
    patient = {
        "patient_id": "P0001",
        "first_name": "Ravi",
        "last_name": "Kumar",
        "date_of_birth": date(1990, 1, 1),
        "sex": "X",
    }
    assert "sex must be M, F or O" in validate_patient(patient)
