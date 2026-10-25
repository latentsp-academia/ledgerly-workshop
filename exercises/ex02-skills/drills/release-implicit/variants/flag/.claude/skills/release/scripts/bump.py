"""Cut a release: bump the patch version in pyproject.toml and open a CHANGELOG entry.

    python3 bump.py LED-105
Prints the new version. Side effects on purpose: this is what a release does.
"""

import re
import sys
from pathlib import Path

ticket = sys.argv[1] if len(sys.argv) > 1 else "unreleased"
py = Path("pyproject.toml")
text = py.read_text()
old = re.search(r'^version = "(\d+)\.(\d+)\.(\d+)"', text, re.M)
if not old:
    sys.exit("no version in pyproject.toml")
major, minor, patch = (int(x) for x in old.groups())
new = f"{major}.{minor}.{patch + 1}"
py.write_text(text.replace(old.group(0), f'version = "{new}"', 1))
log = Path("CHANGELOG.md")
head = log.read_text() if log.exists() else "# Changelog\n"
log.write_text(head.rstrip() + f"\n\n## {new}\n- {ticket}: (release notes go here)\n")
print(new)
