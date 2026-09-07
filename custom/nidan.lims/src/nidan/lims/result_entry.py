"""Result entry and validation engine for NIDAN."""

from decimal import Decimal, InvalidOperation

from .test_catalog import get_test


RESULT_STATES = ("draft", "entered", "verified", "released")


def _as_number(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def validate_result(test_code, parameter_code, value):
    """Validate a result against the configured test parameter definition."""
    test = get_test(test_code)
    if test is None:
        return ["Unknown test"]

    parameter = next((p for p in test["parameters"] if p["code"] == parameter_code), None)
    if parameter is None:
        return ["Unknown parameter"]

    if value is None or str(value).strip() == "":
        return ["Result is required"]

    if parameter["result_type"] == "numeric" and _as_number(value) is None:
        return ["Result must be numeric"]

    return []


def create_result_set(test_code, values):
    """Validate and normalize a complete result payload for a test."""
    test = get_test(test_code)
    if test is None:
        raise ValueError("Unknown test")

    errors = []
    normalized = {}
    for parameter in test["parameters"]:
        code = parameter["code"]
        value = values.get(code)
        parameter_errors = validate_result(test_code, code, value)
        errors.extend("%s: %s" % (code, error) for error in parameter_errors)
        if not parameter_errors:
            normalized[code] = value

    if errors:
        raise ValueError("; ".join(errors))
    return normalized


def can_transition_result(current, target):
    """Validate result lifecycle transitions."""
    transitions = {
        "draft": {"entered"},
        "entered": {"verified", "draft"},
        "verified": {"released", "entered"},
        "released": set(),
    }
    if target not in transitions.get(current, set()):
        raise ValueError("Invalid result transition: %s -> %s" % (current, target))
    return target
