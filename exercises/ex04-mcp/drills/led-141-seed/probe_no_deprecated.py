"""Hidden judge: Ledgerly's own code must not use deprecated library APIs.

Records every warning while importing the app and running its startup, then keeps only the
DeprecationWarnings raised from Ledgerly's source (library-internal noise is ignored).
Catches e.g. FastAPI `@app.on_event` and Pydantic V1 `@validator` / `class Config`.
"""

import os
import sys
import warnings

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    from fastapi.testclient import TestClient

    from ledgerly.api.app import create_app
    from ledgerly.services.store import open_store

    os.environ["LEDGERLY_SEED"] = "1"
    conn = open_store()
    with TestClient(create_app(conn)) as c:
        c.get("/health")
    conn.close()
    os.environ.pop("LEDGERLY_SEED", None)

ours = [
    w for w in caught
    if issubclass(w.category, DeprecationWarning) and "/src/ledgerly/" in str(w.filename).replace("\\", "/")
]
if ours:
    w = ours[0]
    first = str(w.message).strip().splitlines()[0][:90]
    where = str(w.filename).split("/src/")[-1]
    sys.exit(f"{w.category.__name__} at {where}:{w.lineno}: {first}")
print("no deprecated APIs in Ledgerly's code")
