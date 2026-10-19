import sys

from fastapi.testclient import TestClient

from ledgerly.api.app import create_app
from ledgerly.services.store import open_store

client = TestClient(create_app(open_store()), raise_server_exceptions=False)
resp = client.get("/invoices/999")
ctype = resp.headers.get("content-type", "")
if not ctype.startswith("application/problem+json"):
    sys.exit(f"content-type is {ctype!r}, team convention is application/problem+json")
body = resp.json()
missing = [k for k in ("type", "title", "status", "detail") if k not in body]
if missing:
    sys.exit(f"problem body missing {missing}: {body}")
if body["status"] != 404:
    sys.exit(f"problem status {body['status']} != 404")
print("problem+json OK")
