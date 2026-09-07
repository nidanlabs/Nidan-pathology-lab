from nidan.lims.test_catalog import get_test, list_parameters


def test_cbc_has_core_parameters():
    cbc = get_test("cbc")
    assert cbc["name"] == "Complete Blood Count"
    assert cbc["sample_type"] == "EDTA"
    assert {p["code"] for p in cbc["parameters"]} >= {"HB", "WBC", "RBC", "PLT"}


def test_lft_uses_serum():
    assert get_test("LFT")["sample_type"] == "SERUM"


def test_unknown_test_returns_none():
    assert get_test("UNKNOWN") is None


def test_parameter_lookup():
    assert list_parameters("ESR")[0]["unit"] == "mm/hr"
