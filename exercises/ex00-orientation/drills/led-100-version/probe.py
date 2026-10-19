"""Black-box probe for LED-100. Run from ledgerly/: uv run python <this file>."""

import sys
import tomllib
from pathlib import Path

from fastapi.testclient import TestClient

from ledgerly.api.app import create_app
from ledgerly.services.store import open_store

want = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
client = TestClient(create_app(open_store()), raise_server_exceptions=False)
resp = client.get("/version")
if resp.status_code != 200:
    sys.exit(f"GET /version -> {resp.status_code}")
body = resp.json()
if body != {"name": "ledgerly", "version": want}:
    sys.exit(f"GET /version -> {body}, expected name 'ledgerly' and version {want!r}")
print(f"GET /version -> {body}")
