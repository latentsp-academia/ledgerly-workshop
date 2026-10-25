"""Hidden judge for LED-107. Run from ledgerly/: uv run python <this file>.

Team rule (not in the code): amounts are integer cents, a split never loses or invents a cent,
every installment is total // count and the LAST one absorbs the whole remainder.
"""

import sys

from fastapi.testclient import TestClient

from ledgerly.api.app import create_app
from ledgerly.services.store import open_store

client = TestClient(create_app(open_store()), raise_server_exceptions=False)


def invoice(cents: int) -> int:
    body = {
        "customer": "Acme",
        "currency": "USD",
        "vat_rate_bp": 0,
        "lines": [{"description": "Plan", "quantity": 1, "unit_cents": cents}],
    }
    return int(client.post("/invoices", json=body).json()["id"])


CASES = [  # total cents, count, expected installments in cents
    (10_000, 3, [3333, 3333, 3334]),
    (10_000, 7, [1428, 1428, 1428, 1428, 1428, 1428, 1432]),
    (100, 6, [16, 16, 16, 16, 16, 20]),
    (9_999, 1, [9_999]),
]

for total, count, want in CASES:
    inv = invoice(total)
    resp = client.get(f"/invoices/{inv}/installments", params={"count": count})
    if resp.status_code != 200:
        sys.exit(f"{total} cents / {count} -> HTTP {resp.status_code}")
    # one amount per payment: a plain int, or an object with one *_cents field
    got = [
        next((v for k, v in x.items() if k.endswith("_cents")), x) if isinstance(x, dict) else x
        for x in resp.json().get("installments") or []
    ]
    if got != want or not all(type(x) is int for x in got):
        sys.exit(f"{total} cents / {count} -> {got}, expected {want} (integer cents)")

bad = client.get(f"/invoices/{invoice(100)}/installments", params={"count": 0}).status_code
if bad not in (400, 422):
    sys.exit(f"count=0 -> HTTP {bad}, expected 400/422")
print("100.00 / 3 -> [3333, 3333, 3334] ✓ (4 splits + count=0)")
