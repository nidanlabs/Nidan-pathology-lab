"""End-to-end tenant-safe pathology order lifecycle for NIDAN."""

from nidan.lims.auth import require_tenant
from nidan.lims.billing import invoice_with_payment
from nidan.lims.report import build_report
from nidan.lims.report_service import build_verification_token, release_tenant_report
from nidan.lims.workflow import (
    WorkflowError,
    attach_verified_results,
    create_test_order,
    register_patient,
    register_sample,
)


class EndToEndWorkflowError(ValueError):
    """Raised when an end-to-end order cannot advance safely."""


def create_order_with_billing(user, tenant_id, patient, sample, test_ids,
                              billing_items, discount=0, paid=0):
    """Register patient/sample, create test order and attach its invoice."""
    require_tenant(user, tenant_id)
    try:
        scoped_patient = register_patient(user, tenant_id, patient)
        scoped_sample = register_sample(user, tenant_id, sample)
        order = create_test_order(
            user, tenant_id, scoped_patient["patient_id"],
            scoped_sample["sample_id"], test_ids,
        )
        invoice = invoice_with_payment(billing_items, discount=discount, paid=paid)
    except (WorkflowError, ValueError, TypeError, KeyError) as exc:
        raise EndToEndWorkflowError(str(exc))
    order["invoice"] = invoice
    return {
        "tenant_id": tenant_id,
        "patient": scoped_patient,
        "sample": scoped_sample,
        "order": order,
    }


def complete_order_with_report(user, tenant_id, context, results, report_id,
                               remarks=""):
    """Attach verified results, build the report and release it."""
    require_tenant(user, tenant_id)
    if context.get("tenant_id") != tenant_id:
        raise EndToEndWorkflowError("Workflow context belongs to another tenant")
    order = context.get("order")
    if not order:
        raise EndToEndWorkflowError("Order is required")
    try:
        order = attach_verified_results(user, tenant_id, order, results)
        report = build_report({
            "report_id": report_id,
            "patient": context["patient"],
            "sample": context["sample"],
            "results": results,
            "state": "verified",
            "remarks": remarks,
        })
        report["tenant_id"] = tenant_id
        released = release_tenant_report(user, tenant_id, report)
    except (WorkflowError, ValueError, TypeError, KeyError) as exc:
        raise EndToEndWorkflowError(str(exc))
    released["verification_token"] = build_verification_token(
        tenant_id, report_id
    )
    order["status"] = "report_released"
    return {
        "tenant_id": tenant_id,
        "order": order,
        "report": released,
    }
