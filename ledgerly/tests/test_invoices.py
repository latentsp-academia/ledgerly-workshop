import sqlite3

import pytest

from ledgerly.payments.money import Money
from ledgerly.services import invoices as svc


def _lines() -> list[svc.Line]:
    return [svc.Line("Widget", 3, Money(1_000, "USD")), svc.Line("Setup", 1, Money(500, "USD"))]


def test_create_invoice_totals(conn: sqlite3.Connection) -> None:
    inv = svc.create_invoice(conn, "Acme", "USD", _lines())
    assert inv.net == Money(3_500, "USD")
    assert inv.vat == Money(595, "USD")
    assert inv.total == Money(4_095, "USD")
    assert inv.status == "open"


def test_capture_sets_paid(conn: sqlite3.Connection) -> None:
    inv = svc.create_invoice(conn, "Acme", "USD", _lines())
    paid = svc.capture(conn, inv.id)
    assert paid.status == "paid"
    assert paid.captured == paid.total


def test_capture_twice_rejected(conn: sqlite3.Connection) -> None:
    inv = svc.create_invoice(conn, "Acme", "USD", _lines())
    svc.capture(conn, inv.id)
    with pytest.raises(svc.InvoiceStateError):
        svc.capture(conn, inv.id)


def test_empty_invoice_rejected(conn: sqlite3.Connection) -> None:
    with pytest.raises(ValueError, match="at least one line"):
        svc.create_invoice(conn, "Acme", "USD", [])


@pytest.mark.landmine
def test_bulk_invoice_creation(conn: sqlite3.Connection) -> None:
    """Flaky on purpose (~10% of runs): invoice numbers can collide. See LED-118."""
    for i in range(450):
        svc.create_invoice(conn, f"Customer {i}", "USD", _lines())
    assert len(svc.list_invoices(conn)) == 450
