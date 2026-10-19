"""Refund use-cases. Business rules: ADR-0003."""

from __future__ import annotations

import sqlite3

from ledgerly.payments.money import Money
from ledgerly.repo import db
from ledgerly.services.invoices import get_invoice


class RefundError(Exception):
    """A refund violates the refund rules (ADR-0003)."""


def refundable(conn: sqlite3.Connection, invoice_id: int) -> Money:
    """How much can still be refunded on this invoice."""
    invoice = get_invoice(conn, invoice_id)
    already = Money(db.refunded_cents(conn, invoice_id), invoice.captured.currency)
    return invoice.captured - already


def refund_full(conn: sqlite3.Connection, invoice_id: int) -> Money:
    """Refund everything that was captured. Only full refunds are supported today."""
    invoice = get_invoice(conn, invoice_id)
    if invoice.status != "paid":
        raise RefundError(f"Only paid invoices can be refunded (status={invoice.status!r})")
    amount = refundable(conn, invoice_id)
    if amount.cents <= 0:
        raise RefundError("Nothing left to refund")
    db.insert_refund(conn, invoice_id, amount.cents)
    db.set_status(conn, invoice_id, "refunded")
    return amount
