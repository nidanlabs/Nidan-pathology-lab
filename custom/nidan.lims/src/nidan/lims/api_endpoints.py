"""Plone-friendly endpoint helpers.

These helpers are deliberately HTTP-framework neutral. A plone.restapi
resource can call them and serialize the returned dictionaries.
"""

from nidan.lims.auth import require_tenant
from nidan.lims.permissions import require_permission
from nidan.lims.rest_service import patient_resource, sample_resource, report_resource


def create_patient_payload(user, tenant_id, patient):
    require_permission(user, tenant_id, "manage_patients")
    return patient_resource(user, tenant_id, dict(patient, tenant_id=tenant_id))


def create_sample_payload(user, tenant_id, sample):
    require_permission(user, tenant_id, "manage_samples")
    return sample_resource(user, tenant_id, dict(sample, tenant_id=tenant_id))


def read_report_payload(user, tenant_id, report):
    require_tenant(user, tenant_id)
    return report_resource(user, tenant_id, report)
