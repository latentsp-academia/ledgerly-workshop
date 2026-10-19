from __future__ import annotations

import sqlite3

from fastapi import Request


def get_conn(request: Request) -> sqlite3.Connection:
    conn: sqlite3.Connection = request.app.state.conn
    return conn
