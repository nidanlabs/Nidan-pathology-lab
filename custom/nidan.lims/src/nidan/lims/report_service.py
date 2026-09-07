"""Tenant-safe report services and public verification helpers."""

import hashlib

from nidan.lims.auth import require_tenant
from nidan.lims.permissions import require_permission
from nidan.lims.report import release_report


class ReportServiceError(ValueError):
    """Raised when a tenant-safe report operation is invalid."""


def build_verification_token(tenant_id, report_id):
    """Build a deterministic short verification token for a report."""
    value = "%s:%s" % (tenant_id or "", report_id or "")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def _verification_token(report):
    return build_verification_token(
        report.get("tenant_id"), report.get("report_id") or report.get("id")
    )


def release_tenant_report(user, tenant_id, report):
    """Release a verified report only inside its owning tenant."""
    require_tenant(user, tenant_id)
    require_permission(user, tenant_id, "release_reports")
    if report.get("tenant_id") != tenant_id:
        raise ReportServiceError("Report belongs to another tenant")
    try:
        released = release_report(report)
    except (ValueError, TypeError) as exc:
        raise ReportServiceError(str(exc))
    released["verification_token"] = _verification_token(released)
    return released


release_report_for_tenant = release_tenant_report


def public_verification_payload(report):
    """Return only non-sensitive fields needed for public report verification."""
    patient = report.get("patient") or {}
    sample = report.get("sample") or {}
    return {
        "report_id": report.get("report_id") or report.get("id"),
        "patient_id": patient.get("patient_id") or report.get("patient_id"),
        "sample_id": sample.get("sample_id") or report.get("sample_id"),
        "state": report.get("state"),
        "verification_token": report.get("verification_token") or _verification_token(report),
    }
