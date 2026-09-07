"""Tenant-safe commercial pricing and invoicing helpers for NIDAN."""

from decimal import Decimal

from nidan.lims.auth import require_tenant
from nidan.lims.billing import invoice_with_payment, _money


class CommercialBillingError(ValueError):
    """Raised when commercial billing data is invalid."""


def build_test_price(tenant_id, test_id, test_name, price, active=True):
    if not tenant_id:
        raise CommercialBillingError("Tenant ID is required")
    if not test_id or not test_name:
        raise CommercialBillingError("Test ID and name are required")
    if not isinstance(active, bool):
        raise CommercialBillingError("Active flag must be boolean")
    return {
        "tenant_id": tenant_id,
        "test_id": test_id,
        "test_name": test_name,
        "price": _money(price),
        "active": active,
    }


def build_price_catalog(tenant_id, entries):
    if not tenant_id:
        raise CommercialBillingError("Tenant ID is required")
    if not entries:
        raise CommercialBillingError("At least one price entry is required")
    catalog = []
    seen = set()
    for entry in entries:
        if entry.get("tenant_id") != tenant_id:
            raise CommercialBillingError("Price entry belongs to another tenant")
        test_id = entry.get("test_id")
        if test_id in seen:
            raise CommercialBillingError("Duplicate test pricing entry")
        seen.add(test_id)
        catalog.append(dict(entry))
    return catalog


def price_test(catalog, test_id):
    for entry in catalog:
        if entry.get("test_id") == test_id:
            if not entry.get("active", False):
                raise CommercialBillingError("Test price is inactive")
            return entry["price"]
    raise CommercialBillingError("Test price not found")


def build_tenant_invoice(user, tenant_id, invoice_id, items, discount=0, paid=0,
                         currency="INR"):
    require_tenant(user, tenant_id)
    if not invoice_id:
        raise CommercialBillingError("Invoice ID is required")
    if not currency:
        raise CommercialBillingError("Currency is required")
    try:
        invoice = invoice_with_payment(items, discount=discount, paid=paid)
    except (ValueError, TypeError, AttributeError) as exc:
        raise CommercialBillingError(str(exc))
    invoice["invoice_id"] = invoice_id
    invoice["tenant_id"] = tenant_id
    invoice["currency"] = currency
    return invoice
