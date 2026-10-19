import sys

from fastapi.testclient import TestClient

from ledgerly.api.app import create_app
from ledgerly.services.store import open_store

client = TestClient(create_app(open_store()), raise_server_exceptions=False)
resp = client.get("/invoices/999")
if resp.status_code != 404:
    sys.exit(f"GET /invoices/999 -> {resp.status_code}, expected 404")
print("404 OK")
