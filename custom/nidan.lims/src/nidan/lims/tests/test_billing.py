import pytest
from decimal import Decimal

from nidan.lims.billing import calculate_invoice, invoice_with_payment, payment_status


ITEMS = [
    {"code": "CBC", "name": "Complete Blood Count", "quantity": 1, "unit_price": "250"},
    {"code": "LFT", "name": "Liver Function Test", "quantity": 2, "unit_price": "400"},
]


def test_invoice_total_and_discount():
    invoice = calculate_invoice(ITEMS, discount="50")
    assert invoice["subtotal"] == Decimal("1050.00")
    assert invoice["discount"] == Decimal("50.00")
    assert invoice["total"] == Decimal("1000.00")


def test_payment_states():
    assert payment_status("1000", "0") == "unpaid"
    assert payment_status("1000", "400") == "partial"
    assert payment_status("1000", "1000") == "paid"


def test_invoice_with_payment_calculates_due():
    invoice = invoice_with_payment(ITEMS, discount="50", paid="250")
    assert invoice["due"] == Decimal("750.00")
    assert invoice["payment_status"] == "partial"


def test_discount_cannot_exceed_total():
    with pytest.raises(ValueError):
        calculate_invoice(ITEMS, discount="2000")


def test_paid_cannot_exceed_total():
    with pytest.raises(ValueError):
        invoice_with_payment(ITEMS, paid="2000")
