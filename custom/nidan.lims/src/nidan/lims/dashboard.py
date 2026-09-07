"""Tenant-aware dashboard summary contracts for the NIDAN UI."""

from nidan.lims.auth import require_tenant


def build_dashboard(user, tenant_id, metrics=None):
    """Return dashboard metrics only after tenant authorization."""
    require_tenant(user, tenant_id)
    metrics = metrics or {}
    return {
        "tenant_id": tenant_id,
        "patients_today": int(metrics.get("patients_today", 0)),
        "samples_pending": int(metrics.get("samples_pending", 0)),
        "reports_pending": int(metrics.get("reports_pending", 0)),
        "revenue_today": metrics.get("revenue_today", 0),
    }
