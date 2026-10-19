"""Hidden judge: the PR note exists and uses the team's headings."""

import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import prnote  # noqa: E402

text = prnote.read_note()
if text is None:
    sys.exit(f"{prnote.NOTE} not found: the team's PR notes live in docs/pr/<ticket>.md")
secs = prnote.sections(text)
missing = [name for name, pat in prnote.SECTIONS if prnote.find_section(secs, pat) is None]
if missing:
    sys.exit(f"missing house sections: {', '.join(missing)} (has: {', '.join(secs) or 'no ## headings'})")
print("all six house sections present")
