"""Revenue report. LEGACY: still on float dollars via legacy_fx. Rewrite tracked in LED-130."""

from __future__ import annotations

import sqlite3

from ledgerly.payments import legacy_fx
from ledgerly.services.invoices import list_invoices


def revenue_report(conn: sqlite3.Connection, currency: str = "USD") -> dict[str, float]:
    total = 0.0
    for inv in list_invoices(conn):
        if inv.status == "paid":
            dollars = inv.captured.cents / 100
            total += legacy_fx.convert(dollars, inv.captured.currency, currency)
    return {"currency_total": round(total, 2)}
