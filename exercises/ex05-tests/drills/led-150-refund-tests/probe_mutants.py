"""Hidden judge: do the NEW refund tests catch real bugs? (mutation testing, no extra deps)

1. Find the test functions added since `baseline` (the student's / agent's tests).
2. They must pass on the real code.
3. For each mutant, copy the project to a temp dir, plant ONE realistic bug in the refund
   code, and run only the new tests. Failing tests = mutant killed. Passing = it survived.

Green needs MIN_KILLED of the mutants killed. Run from ledgerly/ (the checker does this).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MIN_KILLED = 6
SVC = "src/ledgerly/services/refunds.py"
API = "src/ledgerly/api/routes_refunds.py"

# (id, what the bug is, file, original text, mutated text). Each one breaks an ADR-0003 rule.
MUTANTS = [
    ("M1", "over-refunds allowed (guard removed)", SVC,
     "    if remaining < amount:\n        raise RefundExceedsRemainingError(amount, remaining)\n", ""),
    ("M2", "over-refund silently capped to what's left", SVC,
     "        raise RefundExceedsRemainingError(amount, remaining)", "        amount = remaining"),
    ("M3", "a refused refund (unpaid / nothing left) answers 400, not 409", API,
     "raise HTTPException(status_code=409, detail=str(exc)) from exc",
     "raise HTTPException(status_code=400, detail=str(exc)) from exc"),
    ("M4", "a partial refund marks the invoice fully refunded", SVC,
     'status = "refunded" if amount == remaining else "partially_refunded"', 'status = "refunded"'),
    ("M5", "422 body loses remaining_cents", API,
     'detail={"message": str(exc), "remaining_cents": exc.remaining.cents},', "detail=str(exc),"),
    ("M6", "zero/negative amounts accepted by the service", SVC,
     '    if amount.cents <= 0:\n        raise RefundError("Refund amount must be positive")\n', ""),
    ("M7", "earlier refunds ignored when computing what's left", SVC,
     "    return invoice.captured - already", "    return invoice.captured"),
]


def sh(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)  # noqa: S603


def new_test_names(app: Path) -> list[str]:
    names: list[str] = []
    diff = sh(["git", "diff", "baseline", "--unified=0", "--", "tests"], app).stdout
    names += re.findall(r"^\+\s*def (test_\w+)", diff, re.M)
    untracked = sh(["git", "ls-files", "--others", "--exclude-standard", "--", "tests"], app).stdout
    for rel in untracked.split():
        if rel.endswith(".py"):
            names += re.findall(r"^\s*def (test_\w+)", (app / rel).read_text(), re.M)
    return sorted(set(names))


def run_tests(where: Path, names: list[str]) -> subprocess.CompletedProcess[str]:
    expr = " or ".join(names)
    return sh([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
               "-m", "not landmine", "-k", expr], where)


def main() -> int:
    app = Path.cwd()
    names = new_test_names(app)
    if not names:
        print("no new test functions since baseline: nothing to judge")
        return 1
    base = run_tests(app, names)
    if base.returncode != 0:
        tail = [ln for ln in base.stdout.splitlines() if ln.strip()][-1:] or [""]
        print(f"the new tests fail on the CORRECT code: {tail[0][:90]}")
        return 1

    killed, survived = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for mid, what, rel, old, new in MUTANTS:
            work = Path(tmp) / mid
            shutil.copytree(app, work, ignore=shutil.ignore_patterns(".venv", ".git", "*cache*", "docs"))
            f = work / rel
            text = f.read_text()
            if old not in text:
                survived.append(f"{mid} (code changed, mutant not applicable)")
                continue
            f.write_text(text.replace(old, new, 1))
            (killed if run_tests(work, names).returncode != 0 else survived).append(f"{mid} {what}")

    score = f"{len(killed)}/{len(MUTANTS)} mutants killed by {len(names)} new test(s)"
    if len(killed) >= MIN_KILLED:
        print(score + (f"; survived: {survived[0]}" if survived else ""))
        return 0
    print(f"{score}; survived: " + "; ".join(survived))
    return 1


if __name__ == "__main__":
    sys.exit(main())
