"""Hidden judge for ship-by-arg: the named argument $reviewer landed on the note's first line."""

import sys
from pathlib import Path

note = Path("docs/pr/LED-105.md")
if not note.exists():
    sys.exit("docs/pr/LED-105.md not written: $ticket didn't reach the skill")
first = next((ln for ln in note.read_text().splitlines() if ln.strip()), "")
if "@dana" not in first or "reviewer" not in first.lower():
    sys.exit(f"first line is {first[:60]!r}, expected 'Reviewer: @dana'")
print("docs/pr/LED-105.md · first line: " + first.strip()[:50])
