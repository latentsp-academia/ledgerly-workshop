"""Hash of every file under src/ and tests/ (tracked or not). Run from ledgerly/."""

import hashlib
from pathlib import Path

h = hashlib.sha256()
for p in sorted(Path(".").glob("src/**/*.py")) + sorted(Path(".").glob("tests/**/*.py")):
    h.update(str(p).encode() + b"\0" + p.read_bytes())
print(h.hexdigest())
