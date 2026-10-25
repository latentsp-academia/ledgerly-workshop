"""Hidden judge for release-by-name: /release must still work when typed (0.4.2 -> 0.4.3)."""

import re
import sys
from pathlib import Path

v = re.search(r'^version = "([^"]+)"', Path("pyproject.toml").read_text(), re.M)
log = Path("CHANGELOG.md")
if not v or v.group(1) != "0.4.3":
    sys.exit(f"version is {v.group(1) if v else None!r}, expected 0.4.3: /release didn't run its script")
if not log.exists() or "0.4.3" not in log.read_text() or "go here" in log.read_text():
    sys.exit("CHANGELOG.md has no filled-in 0.4.3 entry")
print("/release LED-105 -> 0.4.3 with notes")
