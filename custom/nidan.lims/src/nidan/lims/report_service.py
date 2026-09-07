"""Tenant-safe report services and public verification helpers."""

import hashlib

from nidan.lims.auth import require_tenant
from nidan.lims.permissions import require_permission
from nidan.lims.report import release_report


def _verification_token(report):
    report_id = report.get("report_id") or report.get("id") or ""
    return hashlib.sha256(str(report_id).encode("utf-8")).hexdigest()[:24]


def release_report_for_tenant(user, tenant_id, report):
    require_tenant(user, tenant_id)
    require_permission(user, tenant_id, "release_reports")
    if report.get("tenant_id") != tenant_id:
        raise ValueError("Report belongs to another tenant")

    released = release_report(report)
    released["verification_token"] = _verification_token(released)
    return released


def public_verification_payload(report):
    """Return only non-sensitive fields needed for public report verification."""
    patient = report.get("patient") or {}
    sample = report.get("sample") or {}
    return {
        "report_id": report.get("report_id") or report.get("id"),
        "patient_id": patient.get("patient_id"),
        "sample_id": sample.get("sample_id"),
        "state": report.get("state"),
        "verification_token": report.get("verification_token") or _verification_token(report),
    }
