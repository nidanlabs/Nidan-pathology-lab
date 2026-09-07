import pytest

from nidan.lims.report import build_report, release_report, validate_report


def payload():
    return {
        "report_id": "RPT-0001",
        "patient": {"patient_id": "P0001", "name": "Test Patient"},
        "sample": {"sample_id": "S0001", "sample_type": "EDTA"},
        "results": [{
            "test_code": "CBC",
            "test_name": "Complete Blood Count",
            "state": "verified",
            "parameters": [{"code": "HB", "value": "12.4", "unit": "g/dL"}],
        }],
        "state": "verified",
    }


def test_report_validation():
    assert validate_report(payload()) == []


def test_build_report_contains_verified_results():
    report = build_report(payload())
    assert report["report_id"] == "RPT-0001"
    assert report["results"][0]["test_code"] == "CBC"


def test_unverified_result_cannot_enter_report():
    data = payload()
    data["results"][0]["state"] = "entered"
    with pytest.raises(ValueError):
        build_report(data)


def test_verified_report_can_be_released():
    report = build_report(payload())
    assert release_report(report)["state"] == "released"
