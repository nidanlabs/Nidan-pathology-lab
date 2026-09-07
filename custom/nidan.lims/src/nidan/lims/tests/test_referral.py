import pytest

from nidan.lims.referral import build_doctor, build_patient_record, validate_doctor


def test_doctor_record():
    doctor = build_doctor({
        "doctor_id": "DR-001",
        "name": "Dr. Test",
        "qualification": "MBBS",
        "specialty": "Medicine",
    })
    assert doctor["doctor_id"] == "DR-001"
    assert doctor["status"] == "active"


def test_doctor_validation():
    assert validate_doctor({"doctor_id": "DR-001", "name": "Dr. Test"}) == []
    with pytest.raises(ValueError):
        build_doctor({"doctor_id": "DR-001", "name": "Dr. Test", "status": "deleted"})


def test_patient_with_referring_doctor():
    patient = build_patient_record({
        "patient_id": "P-001",
        "first_name": "Test",
        "last_name": "Patient",
        "sex": "F",
    }, referring_doctor_id="DR-001")
    assert patient["patient_id"] == "P-001"
    assert patient["referring_doctor_id"] == "DR-001"
