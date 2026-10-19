"""Hidden judge: the note lists the ADRs this diff touches (money → 0001, new route+service → 0002)."""

import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import prnote  # noqa: E402

text = prnote.read_note() or ""
body = prnote.find_section(prnote.sections(text), r"adrs?\b") or ""
need = ["ADR-0001", "ADR-0002"]
missing = [a for a in need if not re.search(a.replace("-", r"[- ]?"), body, re.I)]
if missing:
    sys.exit(f"'ADRs touched' misses {', '.join(missing)} (LED-105 converts money and adds a route + service)")
print("ADR-0001 and ADR-0002 listed")
