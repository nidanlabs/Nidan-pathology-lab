from nidan.lims.content import get_content_type, list_content_types


def test_nidan_content_types_are_declared():
    names = list_content_types()
    assert names == ["NIDANPatient", "NIDANReport", "NIDANSample"]


def test_patient_content_contract():
    spec = get_content_type("NIDANPatient")
    assert spec["portal_type"] == "NIDAN Patient"
    assert "patient_id" in spec["fields"]
    assert "referring_doctor_id" in spec["fields"]


def test_unknown_content_type():
    assert get_content_type("UnknownType") is None
