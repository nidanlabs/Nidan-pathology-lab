"""SENAITE integration boundary for the NIDAN domain workflow.

This module intentionally keeps live Zope/SENAITE imports out of the domain
layer. Production adapters can map these contracts to Dexterity content,
workflows and plone.restapi resources without coupling business rules to
request handling.
"""

from nidan.lims.auth import require_tenant
from nidan.lims.senaite_adapter import SENAITEAdapter


class SENAITEIntegrationError(ValueError):
    """Raised when a SENAITE integration contract is invalid."""


def build_senaite_bundle(user, tenant_id, patient, sample, order, report):
    """Build tenant-scoped SENAITE-compatible payloads for one case."""
    require_tenant(user, tenant_id)
    for record_name, record in (("patient", patient), ("sample", sample),
                                ("order", order), ("report", report)):
        if record.get("tenant_id") != tenant_id:
            raise SENAITEIntegrationError(
                "%s belongs to another tenant" % record_name
            )

    adapter = SENAITEAdapter()
    return {
        "tenant_id": tenant_id,
        "patient": adapter.patient_payload(patient),
        "sample": adapter.sample_payload(sample),
        "order": dict(order),
        "report": adapter.report_payload(report),
    }
