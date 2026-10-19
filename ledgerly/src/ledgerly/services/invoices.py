"""Invoice use-cases."""

from __future__ import annotations

import secrets
import sqlite3
from dataclasses import dataclass

from ledgerly.payments.money import Money
from ledgerly.repo import db
from ledgerly.services.tax import DEFAULT_VAT_RATE_BP, vat_for


@dataclass(frozen=True)
class Line:
    description: str
    quantity: int
    unit: Money


@dataclass(frozen=True)
class Invoice:
    id: int
    number: str
    customer: str
    net: Money
    vat: Money
    status: str
    captured: Money

    @property
    def total(self) -> Money:
        return self.net + self.vat


class InvoiceStateError(Exception):
    """The invoice is not in a state that allows this operation."""


def generate_invoice_number() -> str:
    # Known issue: random numbers can collide under the UNIQUE constraint. See LED-118.
    return f"INV-{secrets.randbelow(999_999) + 1:06d}"


def _from_row(row: sqlite3.Row) -> Invoice:
    cur = row["currency"]
    return Invoice(
        id=row["id"],
        number=row["number"],
        customer=row["customer"],
        net=Money(row["net_cents"], cur),
        vat=Money(row["vat_cents"], cur),
        status=row["status"],
        captured=Money(row["captured_cents"], cur),
    )


def create_invoice(
    conn: sqlite3.Connection,
    customer: str,
    currency: str,
    lines: list[Line],
    vat_rate_bp: int = DEFAULT_VAT_RATE_BP,
) -> Invoice:
    if not lines:
        raise ValueError("An invoice needs at least one line")
    net = Money.zero(currency)
    for line in lines:
        if line.quantity <= 0:
            raise ValueError("Line quantity must be positive")
        net = net + line.unit * line.quantity
    vat = vat_for(net, vat_rate_bp)
    invoice_id = db.insert_invoice(
        conn,
        number=generate_invoice_number(),
        customer=customer,
        currency=currency,
        net_cents=net.cents,
        vat_cents=vat.cents,
        lines=[(ln.description, ln.quantity, ln.unit.cents) for ln in lines],
    )
    return get_invoice(conn, invoice_id)


def get_invoice(conn: sqlite3.Connection, invoice_id: int) -> Invoice:
    row = db.get_invoice(conn, invoice_id)
    if row is None:
        raise KeyError(invoice_id)
    return _from_row(row)


def list_invoices(conn: sqlite3.Connection) -> list[Invoice]:
    return [_from_row(r) for r in db.list_invoices(conn)]


def capture(conn: sqlite3.Connection, invoice_id: int) -> Invoice:
    invoice = get_invoice(conn, invoice_id)
    if invoice.status != "open":
        raise InvoiceStateError(f"Cannot capture an invoice in status {invoice.status!r}")
    db.set_status(conn, invoice_id, "paid", captured_cents=invoice.total.cents)
    return get_invoice(conn, invoice_id)
