"""Connection factory exposed to the API layer, so the API never imports repo directly."""

from __future__ import annotations

import sqlite3

from ledgerly.repo import db


def open_store(url: str = ":memory:") -> sqlite3.Connection:
    return db.connect(url)
