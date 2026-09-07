"""Plone/ZODB persistence adapter for NIDAN records.

This adapter is intentionally thin: the domain layer remains storage
agnostic while Plone/Dexterity objects provide durable ZODB persistence.
The caller supplies a tenant container (normally a Dexterity folder created
for one lab/tenant).
"""

from nidan.lims.auth import require_tenant
from nidan.lims.persistence import PersistenceError


PORTAL_TYPES = {
    "patient": "NIDANPatient",
    "sample": "NIDANSample",
    "report": "NIDANReport",
}


class PloneRepository(object):
    """Tenant-scoped repository backed by Plone Dexterity and ZODB."""

    def __init__(self, container):
        if container is None:
            raise PersistenceError("Plone container is required")
        self.container = container

    def _check_tenant(self, user, tenant_id, record):
        require_tenant(user, tenant_id)
        if record.get("tenant_id") != tenant_id:
            raise PersistenceError("record belongs to another tenant")

    def _portal_type(self, record_type):
        try:
            return PORTAL_TYPES[record_type]
        except KeyError:
            raise PersistenceError("unsupported record type: %s" % record_type)

    def _find(self, record_type, record_id):
        portal_type = self._portal_type(record_type)
        for obj in self.container.values():
            if getattr(obj, "portal_type", None) != portal_type:
                continue
            field_id = getattr(obj, "patient_id", None)
            if record_type == "sample":
                field_id = getattr(obj, "sample_id", None)
            elif record_type == "report":
                field_id = getattr(obj, "report_id", None)
            if field_id == record_id:
                return obj
        return None

    def save(self, user, tenant_id, record_type, record_id, record):
        self._check_tenant(user, tenant_id, record)
        if not record_id:
            raise PersistenceError("record_id is required")

        obj = self._find(record_type, record_id)
        if obj is None:
            from plone import api
            obj = api.content.create(
                container=self.container,
                type=self._portal_type(record_type),
                id=record_id,
                title=record.get("title") or record_id,
            )

        for key, value in record.items():
            if key in ("id", "type"):
                continue
            try:
                setattr(obj, key, value)
            except (AttributeError, TypeError, ValueError):
                raise PersistenceError("unable to persist field: %s" % key)

        obj.reindexObject()
        return self._to_record(obj, tenant_id, record_type)

    def get(self, user, tenant_id, record_type, record_id):
        require_tenant(user, tenant_id)
        obj = self._find(record_type, record_id)
        if obj is None:
            raise PersistenceError("record not found")
        if getattr(obj, "tenant_id", None) != tenant_id:
            raise PersistenceError("record belongs to another tenant")
        return self._to_record(obj, tenant_id, record_type)

    def delete(self, user, tenant_id, record_type, record_id):
        require_tenant(user, tenant_id)
        obj = self._find(record_type, record_id)
        if obj is None:
            raise PersistenceError("record not found")
        if getattr(obj, "tenant_id", None) != tenant_id:
            raise PersistenceError("record belongs to another tenant")
        from plone import api
        api.content.delete(obj=obj)
        return True

    def _to_record(self, obj, tenant_id, record_type):
        result = {
            "id": obj.getId(),
            "type": record_type,
            "tenant_id": tenant_id,
        }
        for field_name in self._field_names(record_type):
            if hasattr(obj, field_name):
                result[field_name] = getattr(obj, field_name)
        return result

    def _field_names(self, record_type):
        fields = {
            "patient": (
                "patient_id", "first_name", "last_name", "date_of_birth", "sex",
                "phone", "address", "referring_doctor_id",
            ),
            "sample": (
                "sample_id", "patient_id", "sample_type", "status", "collection_date",
            ),
            "report": (
                "report_id", "patient_id", "sample_id", "state", "remarks",
            ),
        }
        try:
            return fields[record_type]
        except KeyError:
            raise PersistenceError("unsupported record type: %s" % record_type)
