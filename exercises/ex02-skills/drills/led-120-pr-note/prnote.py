"""Shared helpers for the LED-120 probes: find and parse the PR note in docs/pr/."""

from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path

NOTE = Path("docs/pr/LED-105.md")
if not NOTE.exists():
    # a prompt that never names the ticket (Step 5 evals) may still produce exactly one note
    _notes = sorted(Path("docs/pr").glob("*.md")) if Path("docs/pr").is_dir() else []
    if len(_notes) == 1:
        NOTE = _notes[0]

# house headings, in order (Ex 2 reference.md)
SECTIONS = [
    ("ticket", r"ticket"),
    ("summary", r"summary"),
    ("adrs touched", r"adrs?\b"),
    ("verification", r"verification"),
    ("risk & rollback", r"risk"),
    ("changelog", r"changelog"),
]

GATES = [
    ("tests", r"pytest|\btests?\b", "uv run pytest -q"),
    ("lint", r"ruff check|\blint\b", "uv run ruff check ."),
    ("format", r"ruff format|\bformat\b", "uv run ruff format --check ."),
    ("architecture", r"lint-imports|architecture|import-linter", "uv run lint-imports"),
]


def read_note() -> str | None:
    return NOTE.read_text(errors="replace") if NOTE.exists() else None


def sections(text: str) -> dict[str, str]:
    """Map each '## heading' (lower-cased) to its body."""
    out: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            current = m.group(1).lower()
            out[current] = ""
        elif current is not None:
            out[current] += line + "\n"
    return out


def find_section(secs: dict[str, str], pattern: str) -> str | None:
    for head, body in secs.items():
        if re.search(pattern, head, re.I):
            return body
    return None


def gate_passes(cmd: str) -> bool:
    return subprocess.run(shlex.split(cmd), capture_output=True, text=True).returncode == 0
