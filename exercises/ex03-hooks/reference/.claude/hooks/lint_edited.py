#!/usr/bin/env python3
"""PostToolUse: lint only the file Claude just touched.

Beat one (silent): ruff formats and auto-fixes what it can. Nothing enters the context.
Beat two (talks back): if issues remain, return decision "block" with the errors so the agent
fixes them now, at edit time, not at review time.

Python 3.9+, standard library only. Needs `uv` on PATH (the project's toolchain).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run(args: list, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)  # noqa: S603


def main() -> None:
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ev.get("cwd") or ".").resolve()
    path = (ev.get("tool_input") or {}).get("file_path", "")
    if not path.endswith(".py"):
        sys.exit(0)
    f = Path(path) if Path(path).is_absolute() else root / path
    if not f.exists():
        sys.exit(0)
    target = str(f)

    run(["uv", "run", "--quiet", "ruff", "format", "--quiet", target], root)  # beat one
    run(["uv", "run", "--quiet", "ruff", "check", "--fix", "--quiet", target], root)
    left = run(
        ["uv", "run", "--quiet", "ruff", "check", "--output-format", "concise", target], root
    )
    if left.returncode == 0:
        sys.exit(0)  # silent success

    issues = [ln for ln in left.stdout.splitlines() if ln.strip() and not ln.startswith("Found")]
    print(
        json.dumps(
            {  # beat two
                "decision": "block",
                "reason": "ruff found issues it could not fix automatically. Fix them now:\n"
                + "\n".join(issues[:15]),
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
