#!/usr/bin/env python3
"""PreToolUse fence for Ledgerly. Deterministic: the agent can't talk its way past it.

Reads the hook event (JSON on stdin) and answers with a permission decision:
  deny  never allowed. The reason tells the agent the legitimate route.
  ask   allowed only if a human approves (in headless runs that means: no).
  allow no opinion, so normal permissions apply.

Python 3.9+, standard library only.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------- what is protected

SECRETS = [  # (glob, reason): not even readable
    (".env", "Secrets. Read config from settings, never from .env."),
    (".env.*", "Secrets. Read config from settings, never from .env."),
]
DENY = [  # (glob, reason): readable, never writable, for anyone
    (
        "src/ledgerly/generated/*",
        "Generated code is overwritten on regeneration. Fix it in tracker.yaml.",
    ),
    (".claude/settings.json", "The fence protects itself. Hook changes go through a human PR."),
    (".claude/hooks/*", "The fence protects itself. Hook changes go through a human PR."),
]
ASK: list = [  # (glob, reason): a human decides
    # TODO(you) 1/2: which files may change only with a human's approval?
    # Think: the architecture contract, the lint config, the ADRs, and the VAT module (ADR-0004).
    # Each entry is ("glob", "the reason the agent will read").
    # `python3 tools/hook_test.py fence` tells you when it is right.
]
TESTS = "tests/"
TEST_RULE = (
    "tests/ is append-only: add new tests, never change or delete existing ones. "
    "If an existing test contradicts the request, stop and tell the human which ADR or test "
    "conflicts."
)

# ---------------------------------------------------------------- helpers


def decide(decision: str, reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def rel(root: Path, path: str) -> str | None:
    p = Path(path)
    p = (root / p) if not p.is_absolute() else p
    try:
        return p.resolve().relative_to(root).as_posix()
    except ValueError:
        return None  # outside the project: not this fence's business


def match(path: str, rules: list) -> str | None:
    for pattern, reason in rules:
        if fnmatch.fnmatch(path, pattern):
            return reason
    return None


def applied_migrations(root: Path) -> set:
    out = subprocess.run(  # noqa: S603
        ["git", "ls-files", "migrations"],  # noqa: S607
        cwd=root,
        capture_output=True,
        text=True,
    )
    return {ln.strip() for ln in out.stdout.splitlines() if ln.strip()}


def lines_preserved(old: str, new: str) -> bool:
    """True if every non-blank line of `old` still appears in `new`, in order."""
    want = [ln for ln in old.splitlines() if ln.strip()]
    it = iter(new.splitlines())
    return all(any(ln == got for got in it) for ln in want)


def check_path(root: Path, tool: str, inp: dict) -> tuple[str, str] | None:
    path = inp.get("file_path") or inp.get("notebook_path") or ""
    r = rel(root, path) if path else None
    if r is None:
        return None
    reason = match(r, SECRETS)
    if reason:
        return "deny", f"{r}: {reason}"
    if tool == "Read":
        return None  # reading anything else is fine
    reason = match(r, DENY)
    if reason:
        return "deny", f"{r}: {reason}"
    if r in applied_migrations(root):
        return "deny", f"{r}: applied migrations are immutable. Add a new numbered migration."
    reason = match(r, ASK)
    if reason:
        return "ask", f"{r}: {reason}"
    if r.startswith(TESTS):
        return check_test_edit(root, r, tool, inp)
    return None


def check_test_edit(root: Path, r: str, tool: str, inp: dict) -> tuple[str, str] | None:
    """TODO(you) 2/2: make tests/ append-only.

    Allow: a brand-new test file, and edits that only ADD lines.
    Deny (with TEST_RULE as the reason): any Edit/MultiEdit/Write that changes or removes an
    existing line. Hints: for Edit, compare inp["old_string"] with inp["new_string"]; for Write to
    an existing file, lines_preserved(old_text, inp["content"]) is already written for you.
    """
    return None


WRITES = r"(sed\s+-i|perl\s+-pi|>\s*|mv\s+|rm\s+|truncate\s+)[^|;&]*"
CONFIG = r"(\.importlinter|ruff\.toml|pyproject\.toml|\.claude/)"
BASH_RULES = [  # a regex fence, not a sandbox: it catches the obvious routes around the Edit rules
    (r"\brm\s+-[a-z]*(rf|fr)", "Recursive force delete. Remove specific files, or ask."),
    (r"\bgit\s+push\b.*(--force|-f\b)", "Force push rewrites shared history."),
    (r"\bgit\s+(reset\s+--hard|clean\s+-[a-z]*f|checkout\s+--\s)", "Discards work. Ask the human."),
    (r"(cat|less|more|head|tail|grep|source)\s+[^|;&]*\.env\b", "Secrets. Don't print .env."),
    (WRITES + r"\btests/", TEST_RULE),
    (WRITES + CONFIG, "Protected config. Use Edit so the fence can route it to a human."),
]


def check_bash(cmd: str) -> tuple[str, str] | None:
    for pattern, reason in BASH_RULES:
        if re.search(pattern, cmd):
            return "deny", f"`{cmd[:80]}`: {reason}"
    return None


# ---------------------------------------------------------------- main


def main() -> None:
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # not our event shape: stay out of the way
    tool = ev.get("tool_name", "")
    inp = ev.get("tool_input") or {}
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ev.get("cwd") or ".").resolve()

    # Day 2 hook-in: the test-writer subagent is the one agent allowed to change tests.
    path = rel(root, str(inp.get("file_path", ""))) if inp.get("file_path") else None
    if ev.get("agent_type") == "test-writer" and path and path.startswith(TESTS):
        sys.exit(0)

    verdict = check_bash(inp.get("command", "")) if tool == "Bash" else check_path(root, tool, inp)
    if verdict:
        decide(*verdict)
    sys.exit(0)


if __name__ == "__main__":
    main()
