"""SQLite persistence. Only the services layer may import this module (ADR-0002)."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parents[3] / "migrations"


def connect(url: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(url, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate(conn)
    return conn


def migrate(conn: sqlite3.Connection) -> None:
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        conn.executescript(path.read_text())


def _now() -> str:
    return datetime.now(UTC).isoformat()


def insert_invoice(
    conn: sqlite3.Connection,
    *,
    number: str,
    customer: str,
    currency: str,
    net_cents: int,
    vat_cents: int,
    lines: list[tuple[str, int, int]],
) -> int:
    cur = conn.execute(
        "INSERT INTO invoices (number, customer, currency, net_cents, vat_cents, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (number, customer, currency, net_cents, vat_cents, _now()),
    )
    invoice_id = int(cur.lastrowid or 0)
    conn.executemany(
        "INSERT INTO invoice_lines (invoice_id, description, quantity, unit_cents)"
        " VALUES (?, ?, ?, ?)",
        [(invoice_id, d, q, u) for d, q, u in lines],
    )
    conn.commit()
    return invoice_id


def get_invoice(conn: sqlite3.Connection, invoice_id: int) -> sqlite3.Row | None:
    row: sqlite3.Row | None = conn.execute(
        "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
    ).fetchone()
    return row


def list_invoices(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(conn.execute("SELECT * FROM invoices ORDER BY id"))


def set_status(
    conn: sqlite3.Connection, invoice_id: int, status: str, captured_cents: int | None = None
) -> None:
    if captured_cents is None:
        conn.execute("UPDATE invoices SET status = ? WHERE id = ?", (status, invoice_id))
    else:
        conn.execute(
            "UPDATE invoices SET status = ?, captured_cents = ? WHERE id = ?",
            (status, captured_cents, invoice_id),
        )
    conn.commit()


def insert_refund(conn: sqlite3.Connection, invoice_id: int, amount_cents: int) -> int:
    cur = conn.execute(
        "INSERT INTO refunds (invoice_id, amount_cents, created_at) VALUES (?, ?, ?)",
        (invoice_id, amount_cents, _now()),
    )
    conn.commit()
    return int(cur.lastrowid or 0)


def refunded_cents(conn: sqlite3.Connection, invoice_id: int) -> int:
    row = conn.execute(
        "SELECT COALESCE(SUM(amount_cents), 0) AS total FROM refunds WHERE invoice_id = ?",
        (invoice_id,),
    ).fetchone()
    return int(row["total"])
