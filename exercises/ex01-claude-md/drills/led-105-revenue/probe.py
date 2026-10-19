"""Black-box probe for LED-105. Run from ledgerly/: uv run python <this file>."""

import sys

from fastapi.testclient import TestClient

from ledgerly.api.app import create_app
from ledgerly.services.store import open_store

client = TestClient(create_app(open_store()), raise_server_exceptions=False)


def invoice(currency: str, unit_cents: int, pay: bool) -> None:
    body = {
        "customer": "Probe",
        "currency": currency,
        "lines": [{"description": "x", "quantity": 1, "unit_cents": unit_cents}],
    }
    inv = client.post("/invoices", json=body).json()
    if pay:
        client.post(f"/invoices/{inv['id']}/capture")


invoice("USD", 10_000, pay=True)  # total 11_700 USD -> 10_764 EUR
invoice("EUR", 5_000, pay=True)  # total  5_850 EUR
invoice("USD", 99_999, pay=False)  # open: must be ignored

resp = client.get("/reports/revenue", params={"currency": "EUR"})
if resp.status_code != 200:
    sys.exit(f"GET /reports/revenue -> {resp.status_code}")
body = resp.json()
total = body.get("total_cents")
if not isinstance(total, int):
    sys.exit(f"total_cents must be an int, got {type(total).__name__}: {total!r}")
if total != 16_614:
    sys.exit(f"total_cents = {total}, expected 16614")
if body.get("invoice_count") != 2 or body.get("currency") != "EUR":
    sys.exit(f"unexpected body {body}")
default = client.get("/reports/revenue").json()
if default.get("currency") != "USD":
    sys.exit(f"default currency should be USD, got {default}")
print("endpoint OK: 16614 EUR cents over 2 paid invoices")
