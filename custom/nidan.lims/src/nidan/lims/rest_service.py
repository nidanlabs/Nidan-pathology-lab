"""HTTP/REST-neutral resource serializers."""

from nidan.lims.auth import require_tenant


class RESTServiceError(ValueError):
    """Raised when a record cannot be exposed through the REST layer."""


def _resource(user, tenant_id, record, resource_type, fields):
    require_tenant(user, tenant_id)
    if record.get("tenant_id") != tenant_id:
        raise RESTServiceError("Record belongs to another tenant")

    result = {
        "id": record.get("id"),
        "type": resource_type,
        "tenant_id": tenant_id,
    }
    for field in fields:
        if field in record:
            result[field] = record[field]
    return result


def patient_resource(user, tenant_id, patient):
    return _resource(
        user,
        tenant_id,
        patient,
        "patient",
        ("patient_id", "first_name", "last_name", "date_of_birth", "sex"),
    )


def sample_resource(user, tenant_id, sample):
    return _resource(
        user,
        tenant_id,
        sample,
        "sample",
        ("sample_id", "patient_id", "sample_type", "status"),
    )


def report_resource(user, tenant_id, report):
    return _resource(
        user,
        tenant_id,
        report,
        "report",
        ("report_id", "patient", "sample", "results", "state", "verification_token"),
    )
