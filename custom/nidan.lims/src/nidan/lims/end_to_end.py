"""End-to-end tenant-safe pathology order lifecycle for NIDAN."""

from nidan.lims.auth import require_tenant
from nidan.lims.commercial_billing import build_tenant_invoice
from nidan.lims.permissions import require_permission
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
    """Register patient/sample, create test order and attach a tenant invoice."""
    require_tenant(user, tenant_id)
    require_permission(user, tenant_id, "manage_patients")
    require_permission(user, tenant_id, "manage_samples")
    require_permission(user, tenant_id, "manage_billing")
    try:
        scoped_patient = register_patient(user, tenant_id, patient)
        scoped_sample = register_sample(user, tenant_id, sample)
        order = create_test_order(
            user, tenant_id, scoped_patient["patient_id"],
            scoped_sample["sample_id"], test_ids,
        )
        invoice = build_tenant_invoice(
            user, tenant_id, "INV-%s" % order["sample_id"],
            billing_items, discount=discount, paid=paid,
        )
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
    require_permission(user, tenant_id, "verify_results")
    require_permission(user, tenant_id, "release_reports")
    if context.get("tenant_id") != tenant_id:
        raise EndToEndWorkflowError("Workflow context belongs to another tenant")
    order = context.get("order")
    if not order:
        raise EndToEndWorkflowError("Order is required")

    expected = set(order.get("test_ids", []))
    actual = set(result.get("test_code") for result in results)
    if actual != expected:
        raise EndToEndWorkflowError("Result test codes must exactly match the ordered tests")

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
