"""Tenant-safe commercial LIMS workflow orchestration."""

from nidan.lims.auth import require_tenant, scope_record
from nidan.lims.patient import validate_patient
from nidan.lims.sample import validate_sample


class WorkflowError(ValueError):
    """Raised when a workflow operation cannot be completed."""


def register_patient(user, tenant_id, patient):
    require_tenant(user, tenant_id)
    try:
        validate_patient(patient)
    except (KeyError, TypeError, ValueError) as exc:
        raise WorkflowError(str(exc))
    return scope_record(patient, tenant_id)


def register_sample(user, tenant_id, sample):
    require_tenant(user, tenant_id)
    try:
        validate_sample(sample)
    except (KeyError, TypeError, ValueError) as exc:
        raise WorkflowError(str(exc))
    if sample.get("tenant_id") and sample["tenant_id"] != tenant_id:
        raise WorkflowError("Sample belongs to another tenant")
    return scope_record(sample, tenant_id)


def create_test_order(user, tenant_id, patient_id, sample_id, test_ids):
    require_tenant(user, tenant_id)
    if not patient_id or not sample_id or not test_ids:
        raise WorkflowError("patient_id, sample_id and test_ids are required")
    return {
        "tenant_id": tenant_id,
        "patient_id": patient_id,
        "sample_id": sample_id,
        "test_ids": list(test_ids),
        "status": "ordered",
    }


def attach_verified_results(user, tenant_id, order, results):
    require_tenant(user, tenant_id)
    if order.get("tenant_id") != tenant_id:
        raise WorkflowError("Order belongs to another tenant")
    if not results:
        raise WorkflowError("At least one result is required")
    for result in results:
        if result.get("state") != "verified":
            raise WorkflowError("Only verified results can be attached")
    updated = dict(order)
    updated["results"] = list(results)
    updated["status"] = "results_verified"
    return updated
