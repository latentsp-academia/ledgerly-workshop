"""Hidden judge: preparing a PR note must not change code beyond the LED-105 setup."""

import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[4]
setup = root / "exercises/ex01-claude-md/drills/led-105-revenue/reference/green.patch"


def numstat(args: list[str]) -> set[str]:
    out = subprocess.run(args, capture_output=True, text=True).stdout
    return {ln for ln in out.splitlines() if ln.strip()}


subprocess.run(["git", "add", "-N", "src", "tests"], capture_output=True)  # count new files too
now = numstat(["git", "diff", "baseline", "--numstat", "--", "src", "tests"])
subprocess.run(["git", "reset", "-q"], capture_output=True)
expected = numstat(["git", "apply", "--numstat", str(setup)])
extra = sorted(now - expected)
if extra:
    sys.exit("code changed while writing the note: " + ", ".join(x.split("\t")[-1] for x in extra))
print("only docs/ changed")
