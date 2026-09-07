"""Tenant-safe report release and public verification contracts."""

import hashlib

from nidan.lims.auth import require_tenant
from nidan.lims.report import release_report


class ReportServiceError(ValueError):
    """Raised when a report operation is invalid."""


def release_tenant_report(user, tenant_id, report):
    """Release a verified report only inside its owning tenant."""
    require_tenant(user, tenant_id)
    if report.get("tenant_id") != tenant_id:
        raise ReportServiceError("Report belongs to another tenant")
    try:
        return release_report(report)
    except (KeyError, TypeError, ValueError) as exc:
        raise ReportServiceError(str(exc))


def build_verification_token(tenant_id, report_id, report_version="1"):
    """Create a deterministic non-secret lookup token for a report.

    The token is not an authentication credential. Public verification must
    still enforce rate limiting and expose only the minimum report metadata.
    """
    if not tenant_id or not report_id:
        raise ReportServiceError("tenant_id and report_id are required")
    raw = "%s:%s:%s" % (tenant_id, report_id, report_version)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def public_verification_payload(report):
    """Return only safe metadata for QR/public report verification."""
    return {
        "report_id": report.get("report_id"),
        "patient_id": report.get("patient_id"),
        "sample_id": report.get("sample_id"),
        "state": report.get("state"),
        "generated_at": report.get("generated_at"),
    }
