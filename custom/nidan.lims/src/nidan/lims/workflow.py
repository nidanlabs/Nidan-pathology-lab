"""Tenant-safe commercial LIMS workflow orchestration."""

from nidan.lims.api import validate_patient
from nidan.lims.auth import require_tenant, scope_record
from nidan.lims.permissions import require_permission
from nidan.lims.sample import validate_sample


class WorkflowError(ValueError):
    """Raised when a workflow operation cannot be completed."""


def _validate_or_raise(errors):
    if errors:
        raise WorkflowError("; ".join(errors))


def register_patient(user, tenant_id, patient):
    require_tenant(user, tenant_id)
    require_permission(user, tenant_id, "manage_patients")
    _validate_or_raise(validate_patient(patient))
    if patient.get("tenant_id") and patient["tenant_id"] != tenant_id:
        raise WorkflowError("Patient belongs to another tenant")
    return scope_record(patient, tenant_id)


def register_sample(user, tenant_id, sample):
    require_tenant(user, tenant_id)
    require_permission(user, tenant_id, "manage_samples")
    _validate_or_raise(validate_sample(sample))
    if sample.get("tenant_id") and sample["tenant_id"] != tenant_id:
        raise WorkflowError("Sample belongs to another tenant")
    return scope_record(sample, tenant_id)


def create_test_order(user, tenant_id, patient_id, sample_id, test_ids):
    require_tenant(user, tenant_id)
    require_permission(user, tenant_id, "manage_tests")
    if not patient_id or not sample_id or not test_ids:
        raise WorkflowError("patient_id, sample_id and test_ids are required")
    if len(set(test_ids)) != len(test_ids):
        raise WorkflowError("Duplicate test IDs are not allowed")
    return {
        "tenant_id": tenant_id,
        "patient_id": patient_id,
        "sample_id": sample_id,
        "test_ids": list(test_ids),
        "status": "ordered",
    }


def attach_verified_results(user, tenant_id, order, results):
    require_tenant(user, tenant_id)
    require_permission(user, tenant_id, "verify_results")
    if order.get("tenant_id") != tenant_id:
        raise WorkflowError("Order belongs to another tenant")
    if not results:
        raise WorkflowError("At least one result is required")
    expected = set(order.get("test_ids", []))
    actual = set(result.get("test_code") for result in results)
    if actual != expected:
        raise WorkflowError("Results do not match ordered tests")
    for result in results:
        if result.get("state") != "verified":
            raise WorkflowError("Only verified results can be attached")
    updated = dict(order)
    updated["results"] = list(results)
    updated["status"] = "results_verified"
    return updated
