from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get_invoice(client: TestClient) -> None:
    created = client.post(
        "/invoices",
        json={
            "customer": "Acme",
            "currency": "EUR",
            "lines": [{"description": "Consulting", "quantity": 1, "unit_cents": 10_000}],
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["total_cents"] == 11_700
    fetched = client.get(f"/invoices/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["number"] == body["number"]


def test_capture(client: TestClient, paid_invoice: dict) -> None:  # type: ignore[type-arg]
    assert paid_invoice["status"] == "paid"
    assert paid_invoice["captured_cents"] == 11_700


def test_full_refund(client: TestClient, paid_invoice: dict) -> None:  # type: ignore[type-arg]
    resp = client.post(f"/invoices/{paid_invoice['id']}/refund")
    assert resp.status_code == 200
    assert resp.json()["refunded_cents"] == 11_700


def test_refund_twice_conflicts(client: TestClient, paid_invoice: dict) -> None:  # type: ignore[type-arg]
    client.post(f"/invoices/{paid_invoice['id']}/refund")
    assert client.post(f"/invoices/{paid_invoice['id']}/refund").status_code == 409
