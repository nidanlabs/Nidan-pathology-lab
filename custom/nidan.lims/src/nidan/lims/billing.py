"""Billing and payment calculation helpers for NIDAN."""

from decimal import Decimal, InvalidOperation


PAYMENT_STATES = ("unpaid", "partial", "paid", "refunded")


def _money(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid monetary amount")
    if amount < 0:
        raise ValueError("Monetary amount cannot be negative")
    return amount.quantize(Decimal("0.01"))


def calculate_invoice(items, discount=0):
    """Calculate invoice totals without applying tax or clinical assumptions."""
    if not items:
        raise ValueError("At least one billing item is required")

    normalized = []
    subtotal = Decimal("0.00")
    for item in items:
        code = item.get("code")
        name = item.get("name")
        quantity = int(item.get("quantity", 1))
        if not code or not name:
            raise ValueError("Billing item code and name are required")
        if quantity <= 0:
            raise ValueError("Billing quantity must be positive")
        unit_price = _money(item.get("unit_price"))
        line_total = (unit_price * quantity).quantize(Decimal("0.01"))
        subtotal += line_total
        normalized.append({
            "code": code,
            "name": name,
            "quantity": quantity,
            "unit_price": unit_price,
            "line_total": line_total,
        })

    discount = _money(discount)
    if discount > subtotal:
        raise ValueError("Discount cannot exceed subtotal")

    total = (subtotal - discount).quantize(Decimal("0.01"))
    return {
        "items": normalized,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
    }


def payment_status(total, paid):
    """Return the payment state for an invoice."""
    total = _money(total)
    paid = _money(paid)
    if paid > total:
        raise ValueError("Paid amount cannot exceed invoice total")
    if paid == Decimal("0.00"):
        return "unpaid"
    if paid == total:
        return "paid"
    return "partial"


def invoice_with_payment(items, discount=0, paid=0):
    invoice = calculate_invoice(items, discount=discount)
    paid = _money(paid)
    invoice["paid"] = paid
    invoice["due"] = (invoice["total"] - paid).quantize(Decimal("0.01"))
    invoice["payment_status"] = payment_status(invoice["total"], paid)
    return invoice
