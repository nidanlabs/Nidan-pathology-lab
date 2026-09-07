import pytest
from decimal import Decimal

from nidan.lims.auth import build_user
from nidan.lims.commercial_billing import (
    CommercialBillingError,
    build_price_catalog,
    build_test_price,
    build_tenant_invoice,
    price_test,
)


TENANT = "lab-001"
USER = build_user("user-1", TENANT, "owner@nidan.test", role="owner")


def test_test_price_and_catalog():
    entry = build_test_price(TENANT, "CBC", "Complete Blood Count", "250")
    catalog = build_price_catalog(TENANT, [entry])
    assert price_test(catalog, "CBC") == Decimal("250.00")


def test_duplicate_test_price_rejected():
    first = build_test_price(TENANT, "CBC", "Complete Blood Count", "250")
    second = build_test_price(TENANT, "CBC", "Complete Blood Count", "300")
    with pytest.raises(CommercialBillingError):
        build_price_catalog(TENANT, [first, second])


def test_inactive_price_rejected():
    entry = build_test_price(TENANT, "CBC", "Complete Blood Count", "250", active=False)
    with pytest.raises(CommercialBillingError):
        price_test([entry], "CBC")


def test_cross_tenant_price_rejected():
    entry = build_test_price("lab-002", "CBC", "Complete Blood Count", "250")
    with pytest.raises(CommercialBillingError):
        build_price_catalog(TENANT, [entry])


def test_tenant_invoice_is_scoped():
    invoice = build_tenant_invoice(
        USER,
        TENANT,
        "INV-1001",
        [{"code": "CBC", "name": "Complete Blood Count", "quantity": 1, "unit_price": "250"}],
        paid="100",
    )
    assert invoice["tenant_id"] == TENANT
    assert invoice["invoice_id"] == "INV-1001"
    assert invoice["currency"] == "INR"
    assert invoice["due"] == Decimal("150.00")
    assert invoice["payment_status"] == "partial"


def test_cross_tenant_invoice_denied():
    with pytest.raises(Exception):
        build_tenant_invoice(
            USER,
            "lab-002",
            "INV-1002",
            [{"code": "CBC", "name": "Complete Blood Count", "quantity": 1, "unit_price": "250"}],
        )
