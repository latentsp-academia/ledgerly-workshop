"""Seeding works when LEDGERLY_SEED=1 and only then (runs the app's startup via TestClient)."""

import os
import sys

from fastapi.testclient import TestClient

from ledgerly.api.app import create_app
from ledgerly.services.store import open_store

os.environ.pop("LEDGERLY_SEED", None)
plain = open_store()
with TestClient(create_app(plain)) as c:
    seeded_without = c.get("/invoices").json()
plain.close()
if seeded_without:
    sys.exit("invoices were seeded without LEDGERLY_SEED=1")
os.environ["LEDGERLY_SEED"] = "1"
seeded = open_store()
with TestClient(create_app(seeded)) as c:
    inv = c.get("/invoices").json()
seeded.close()
os.environ.pop("LEDGERLY_SEED", None)
if len(inv) != 2:
    sys.exit(f"expected 2 seeded invoices with LEDGERLY_SEED=1, got {len(inv)}")
statuses = sorted((i["customer"], i["status"]) for i in inv)
if statuses != [("Demo Co", "paid"), ("Sample GmbH", "open")]:
    sys.exit(f"unexpected seed: {statuses}")
print("seeding works, and only with LEDGERLY_SEED=1")
