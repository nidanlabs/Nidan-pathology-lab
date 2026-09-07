"""Persistence boundary for NIDAN records.

The domain layer stays storage-agnostic. This repository contract is the
small interface that a Plone/SENAITE adapter can implement using persistent
content objects.
"""

from nidan.lims.auth import AuthError, require_tenant


class PersistenceError(ValueError):
    """Raised for invalid persistence operations."""


class TenantRepository(object):
    """Minimal tenant-scoped repository interface."""

    def __init__(self):
        self._records = {}

    def save(self, user, tenant_id, record_type, record_id, record):
        try:
            require_tenant(user, tenant_id)
        except AuthError as exc:
            raise PersistenceError(str(exc))
        if record.get("tenant_id") != tenant_id:
            raise PersistenceError("record belongs to another tenant")
        if not record_id:
            raise PersistenceError("record_id is required")
        key = (tenant_id, record_type, record_id)
        self._records[key] = dict(record)
        return dict(self._records[key])

    def get(self, user, tenant_id, record_type, record_id):
        require_tenant(user, tenant_id)
        key = (tenant_id, record_type, record_id)
        record = self._records.get(key)
        if record is None:
            raise PersistenceError("record not found")
        return dict(record)
