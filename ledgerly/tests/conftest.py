from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ledgerly.api.app import create_app
from ledgerly.services.store import open_store


@pytest.fixture
def conn() -> Iterator[sqlite3.Connection]:
    c = open_store()
    yield c
    c.close()


@pytest.fixture
def client(conn: sqlite3.Connection) -> TestClient:
    return TestClient(create_app(conn))


@pytest.fixture
def paid_invoice(client: TestClient) -> dict:  # type: ignore[type-arg]
    created = client.post(
        "/invoices",
        json={
            "customer": "Acme",
            "currency": "USD",
            "lines": [{"description": "Widget", "quantity": 2, "unit_cents": 5_000}],
        },
    ).json()
    return client.post(f"/invoices/{created['id']}/capture").json()  # type: ignore[no-any-return]
