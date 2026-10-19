from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ledgerly.api.deps import get_conn
from ledgerly.api.schemas import InvoiceIn, InvoiceOut
from ledgerly.payments.money import Money
from ledgerly.services import invoices as svc

router = APIRouter(prefix="/invoices", tags=["invoices"])
Conn = Annotated[sqlite3.Connection, Depends(get_conn)]


def to_out(inv: svc.Invoice) -> InvoiceOut:
    return InvoiceOut(
        id=inv.id,
        number=inv.number,
        customer=inv.customer,
        currency=inv.net.currency,
        status=inv.status,
        net_cents=inv.net.cents,
        vat_cents=inv.vat.cents,
        total_cents=inv.total.cents,
        captured_cents=inv.captured.cents,
    )


@router.post("", status_code=201, response_model=InvoiceOut)
def create_invoice(body: InvoiceIn, conn: Conn) -> InvoiceOut:
    try:
        lines = [
            svc.Line(ln.description, ln.quantity, Money(ln.unit_cents, body.currency))
            for ln in body.lines
        ]
        inv = svc.create_invoice(conn, body.customer, body.currency, lines, body.vat_rate_bp)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return to_out(inv)


@router.get("", response_model=list[InvoiceOut])
def list_invoices(conn: Conn) -> list[InvoiceOut]:
    return [to_out(i) for i in svc.list_invoices(conn)]


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, conn: Conn) -> InvoiceOut:
    return to_out(svc.get_invoice(conn, invoice_id))


@router.post("/{invoice_id}/capture", response_model=InvoiceOut)
def capture(invoice_id: int, conn: Conn) -> InvoiceOut:
    try:
        return to_out(svc.capture(conn, invoice_id))
    except svc.InvoiceStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
