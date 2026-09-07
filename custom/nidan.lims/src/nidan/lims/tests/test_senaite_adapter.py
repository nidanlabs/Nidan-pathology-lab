from nidan.lims.senaite_adapter import SENAITEAdapter


def test_patient_payload_maps_nidan_fields():
    payload = SENAITEAdapter().patient_payload({
        "patient_id": "P-001",
        "first_name": "Test",
        "last_name": "Patient",
        "sex": "F",
        "phone": "9999999999",
    })
    assert payload["patient_id"] == "P-001"
    assert payload["sex"] == "F"


def test_sample_payload_defaults_status():
    payload = SENAITEAdapter().sample_payload({
        "sample_id": "S-001",
        "patient_id": "P-001",
        "sample_type": "SERUM",
    })
    assert payload["status"] == "registered"


def test_result_and_report_payloads_are_serializable_mappings():
    adapter = SENAITEAdapter()
    result = adapter.result_payload({
        "test_code": "CBC",
        "parameters": [{"code": "HB", "value": "12.5"}],
        "state": "verified",
    })
    report = adapter.report_payload({
        "report_id": "RPT-001",
        "patient": {"patient_id": "P-001"},
        "sample": {"sample_id": "S-001"},
        "results": [result],
        "state": "verified",
    })
    assert report["report_id"] == "RPT-001"
    assert report["results"][0]["test_code"] == "CBC"
