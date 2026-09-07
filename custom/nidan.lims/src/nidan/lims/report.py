"""Professional pathology report assembly for NIDAN."""

from datetime import datetime


REPORT_STATES = ("draft", "verified", "released")


def validate_report(payload):
    """Validate the minimum data required to assemble a report."""
    errors = []
    for field in ("report_id", "patient", "sample", "results"):
        if not payload.get(field):
            errors.append("%s is required" % field)
    return errors


def build_report(payload):
    """Build a deterministic report document model from verified results.

    This produces data for a later PDF/HTML renderer; it does not make a
    clinical interpretation or alter laboratory results.
    """
    errors = validate_report(payload)
    if errors:
        raise ValueError("; ".join(errors))

    state = payload.get("state", "draft")
    if state not in REPORT_STATES:
        raise ValueError("Invalid report state")

    results = []
    for result in payload["results"]:
        if result.get("state") != "verified":
            raise ValueError("All results must be verified before report release")
        results.append({
            "test_code": result.get("test_code"),
            "test_name": result.get("test_name"),
            "parameters": list(result.get("parameters", [])),
        })

    return {
        "report_id": payload["report_id"],
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "patient": dict(payload["patient"]),
        "sample": dict(payload["sample"]),
        "results": results,
        "state": state,
        "remarks": payload.get("remarks", ""),
    }


def release_report(report):
    """Release a verified report model."""
    if report.get("state") != "verified":
        raise ValueError("Only verified reports can be released")
    released = dict(report)
    released["state"] = "released"
    return released
