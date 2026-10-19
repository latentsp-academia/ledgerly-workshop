#!/usr/bin/env python3
"""Run Ledgerly's four quality gates and print a markdown table.

Called from SKILL.md as dynamic context: !`python3 ${CLAUDE_SKILL_DIR}/scripts/gates.py`
Scripts are run, not loaded: only this table enters the context, not this file.
Note: this file lives in the repo, so ruff lints it like any other code.
"""

import shlex
import subprocess
import sys

GATES = [
    ("tests", "uv run pytest -q"),
    ("lint", "uv run ruff check ."),
    ("format", "uv run ruff format --check ."),
    ("architecture", "uv run lint-imports"),
]


def run(cmd: str, cwd: str = ".") -> subprocess.CompletedProcess[str]:
    # fixed commands from GATES above, never user input
    return subprocess.run(shlex.split(cmd), cwd=cwd, capture_output=True, text=True)  # noqa: S603


def last_line(out: str) -> str:
    lines = [ln.strip() for ln in out.strip().splitlines() if ln.strip() and "warning:" not in ln]
    return (lines[-1] if lines else "")[:80].replace("|", "/")


def main() -> int:
    root = run("git rev-parse --show-toplevel").stdout.strip() or "."
    print("| gate | command | result | detail |")
    print("|---|---|---|---|")
    failed = 0
    for name, cmd in GATES:
        proc = run(cmd, cwd=root)
        ok = proc.returncode == 0
        failed += not ok
        verdict = "✅ pass" if ok else "❌ FAIL"
        print(f"| {name} | `{cmd}` | {verdict} | {last_line(proc.stdout + proc.stderr)} |")
    print(f"\n{len(GATES) - failed}/{len(GATES)} gates green.")
    return 0  # never fail the skill load; the table carries the verdict


if __name__ == "__main__":
    sys.exit(main())
