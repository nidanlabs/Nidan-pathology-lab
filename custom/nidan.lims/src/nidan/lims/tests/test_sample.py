from datetime import date

import pytest

from nidan.lims.sample import next_sample_status, validate_sample


def valid_sample():
    return {
        "sample_id": "S0001",
        "patient_id": "P0001",
        "sample_type": "EDTA",
        "collection_date": date(2026, 9, 7),
        "status": "registered",
    }


def test_validate_sample_accepts_valid_payload():
    assert validate_sample(valid_sample()) == []


def test_validate_sample_rejects_unknown_type():
    sample = valid_sample()
    sample["sample_type"] = "UNKNOWN"
    assert "sample_type is invalid" in validate_sample(sample)


def test_sample_workflow_allows_normal_transition():
    assert next_sample_status("registered", "collected") == "collected"
    assert next_sample_status("collected", "received") == "received"
    assert next_sample_status("received", "processing") == "processing"
    assert next_sample_status("processing", "completed") == "completed"


def test_sample_workflow_rejects_invalid_transition():
    with pytest.raises(ValueError):
        next_sample_status("registered", "completed")
