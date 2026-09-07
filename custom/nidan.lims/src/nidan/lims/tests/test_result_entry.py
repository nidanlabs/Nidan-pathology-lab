import pytest

from nidan.lims.result_entry import (
    can_transition_result,
    create_result_set,
    validate_result,
)


def test_numeric_result_validation():
    assert validate_result("CBC", "HB", "12.4") == []
    assert validate_result("CBC", "HB", "abc") == ["Result must be numeric"]


def test_unknown_parameter():
    assert validate_result("CBC", "NOT_A_PARAMETER", "1") == ["Unknown parameter"]


def test_complete_cbc_result_set():
    values = {code: "1" for code in ("HB", "WBC", "RBC", "PLT", "HCT", "MCV", "MCH", "MCHC", "RDW_CV")}
    assert len(create_result_set("CBC", values)) == 9


def test_incomplete_result_set_is_rejected():
    with pytest.raises(ValueError):
        create_result_set("CBC", {"HB": "12"})


def test_result_lifecycle():
    assert can_transition_result("draft", "entered") == "entered"
    assert can_transition_result("entered", "verified") == "verified"
    assert can_transition_result("verified", "released") == "released"
