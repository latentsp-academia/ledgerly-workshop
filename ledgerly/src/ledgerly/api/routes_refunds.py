"""Refund endpoints.

LEGACY: written before the services layer existed, so it talks to the database directly
and duplicates the refund rules. New refund behaviour belongs in services/refunds.py.
"""

from __future__ import annotations

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ledgerly.api.deps import get_conn
from ledgerly.api.schemas import RefundOut
from ledgerly.repo import db

router = APIRouter(prefix="/invoices", tags=["refunds"])
Conn = Annotated[sqlite3.Connection, Depends(get_conn)]


@router.post("/{invoice_id}/refund", response_model=RefundOut)
def refund(invoice_id: int, conn: Conn) -> RefundOut:
    row = db.get_invoice(conn, invoice_id)
    if row is None:
        raise HTTPException(status_code=404, detail="invoice not found")
    if row["status"] != "paid":
        raise HTTPException(status_code=409, detail="only paid invoices can be refunded")
    amount = row["captured_cents"] - db.refunded_cents(conn, invoice_id)
    if amount <= 0:
        raise HTTPException(status_code=409, detail="nothing left to refund")
    db.insert_refund(conn, invoice_id, amount)
    db.set_status(conn, invoice_id, "refunded")
    return RefundOut(invoice_id=invoice_id, refunded_cents=amount, currency=row["currency"])
