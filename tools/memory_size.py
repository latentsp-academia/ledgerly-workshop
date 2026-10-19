#!/usr/bin/env python3
"""Approximate what your memory files cost, including everything pulled in by @imports.

    python3 tools/memory_size.py                 # ledgerly/ root CLAUDE.md (+ CLAUDE.local.md)
    python3 tools/memory_size.py path/to/CLAUDE.md

Tokens are estimated as characters / 4. Use /context in Claude Code for the real number;
this script exists so you can compare variants without starting a session.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional, Set

ROOT = Path(__file__).resolve().parents[1]
IMPORT = re.compile(r"^\s*@(\S+)\s*$")


def expand(path: Path, seen: Set[Path], depth: int = 0, rows: Optional[List] = None) -> List:
    rows = [] if rows is None else rows
    path = path.resolve()
    if path in seen or not path.exists():
        return rows
    seen.add(path)
    text = path.read_text(errors="replace")
    rows.append((depth, path, len(text.splitlines()), len(text) // 4))
    in_code = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        m = None if in_code else IMPORT.match(line)
        if m and depth < 5:
            target = Path(m.group(1)).expanduser()
            if not target.is_absolute():
                target = path.parent / target
            expand(target, seen, depth + 1, rows)
    return rows


def main() -> None:
    targets = [Path(a) for a in sys.argv[1:]] or [
        p for p in (ROOT / "ledgerly" / "CLAUDE.md", ROOT / "ledgerly" / "CLAUDE.local.md") if p.exists()
    ]
    if not targets:
        print("no CLAUDE.md found in ledgerly/ (that's Step 0 of Exercise 1)")
        return
    total_tokens = 0
    for t in targets:
        for depth, p, lines, tokens in expand(t, set()):
            total_tokens += tokens
            label = ("  " * depth + ("@ " if depth else "") + str(p.relative_to(ROOT) if ROOT in p.parents else p))
            print(f"{label:<70} {lines:>5} lines  ~{tokens:>6,} tokens")
    print(f"{'TOTAL loaded at session start':<70} {'':>11}  ~{total_tokens:>6,} tokens")


if __name__ == "__main__":
    main()
