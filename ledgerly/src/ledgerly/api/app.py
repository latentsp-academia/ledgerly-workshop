from __future__ import annotations

import sqlite3

from fastapi import FastAPI

from ledgerly.api import routes_invoices, routes_refunds
from ledgerly.services.store import open_store


def create_app(conn: sqlite3.Connection | None = None) -> FastAPI:
    app = FastAPI(title="Ledgerly", version="0.4.2")
    app.state.conn = conn if conn is not None else open_store()
    app.include_router(routes_invoices.router)
    app.include_router(routes_refunds.router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
