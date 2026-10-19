#!/usr/bin/env python3
"""Stop hook: the agent can't say "done" until the four gates are green.

  no code changed       → allow (questions and reviews aren't gated)
  all 4 gates green     → allow
  a gate is red         → block with the reason (the agent keeps working)
  red 3 times in a row  → allow, with a warning (the stop rule: never loop forever)

Attempts are counted per session in .claude/state/ (git-ignored).
Python 3.9+, standard library only. Needs `uv` on PATH.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

MAX_ATTEMPTS = 3
GATES = [
    ("tests", "uv run pytest -q"),
    ("lint", "uv run ruff check ."),
    ("format", "uv run ruff format --check ."),
    ("architecture", "uv run lint-imports"),
]
NOT_CODE = (".claude/", "docs/", "CLAUDE.md", "CLAUDE.local.md", ".mcp.json")


def code_changed(root: Path) -> bool:
    out = subprocess.run(  # noqa: S603
        ["git", "status", "--porcelain"],  # noqa: S607
        cwd=root,
        capture_output=True,
        text=True,
    ).stdout
    paths = [ln[3:].strip().strip('"') for ln in out.splitlines() if ln.strip()]
    return any(not p.startswith(NOT_CODE) and not p.endswith("CLAUDE.md") for p in paths)


def last_line(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and "warning:" not in ln]
    return lines[-1][:120] if lines else ""


def main() -> None:
    try:
        ev = json.load(sys.stdin)
    except Exception:
        ev = {}
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ev.get("cwd") or ".").resolve()
    if not code_changed(root):
        sys.exit(0)

    state_file = root / ".claude" / "state" / "finish_line.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    sid = ev.get("session_id", "default")

    failed = []
    for name, cmd in GATES:
        proc = subprocess.run(shlex.split(cmd), cwd=root, capture_output=True, text=True)  # noqa: S603
        if proc.returncode != 0:
            failed.append(f"{name} (`{cmd}`): {last_line(proc.stdout + proc.stderr)}")

    if not failed:
        state.pop(sid, None)
        result = {"systemMessage": "✅ finish line: 4/4 gates green"}
    else:
        attempts = state.get(sid, 0) + 1
        state[sid] = attempts
        # TODO(you): the stop rule. As written this blocks forever on a red gate.
        # After MAX_ATTEMPTS, let the agent stop and warn the human instead.
        if True:
            result = {
                "decision": "block",
                "reason": (
                    f"Finish line not met (attempt {attempts}/{MAX_ATTEMPTS}). Red gates:\n- "
                    + "\n- ".join(failed)
                    + "\nFix the cause. If a failing test contradicts an ADR or the request, "
                    "stop and say so instead of working around it."
                ),
            }
        else:
            state.pop(sid, None)
            result = {
                "systemMessage": f"⚠️ finish line: stopped with {len(failed)} red gate(s) after "
                f"{MAX_ATTEMPTS} attempts. A human needs to look."
            }

    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state))
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
