#!/usr/bin/env python3
"""Test a hook before you wire it: feed it events, check its decisions.

    python3 tools/hook_test.py fence            # exercises/ex03-hooks/hooktests/fence.json
    python3 tools/hook_test.py lint finish      # several suites
    python3 tools/hook_test.py all

Each case pipes a JSON event into the hook script (in ledgerly/.claude/hooks/, i.e. YOUR hook)
and reads the outcome the way Claude Code does:

  deny / ask / allow   PreToolUse hookSpecificOutput.permissionDecision
  block                {"decision": "block"} or exit code 2
  pass                 exit 0 with no decision (allowed, nothing to say)

A check that cannot fail is not evidence: most cases here are ones that must go RED.
Standard library only.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ledgerly"
SUITES = ROOT / "exercises" / "ex03-hooks" / "hooktests"
TTY = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
G, R, D, X = ("\033[32m", "\033[31m", "\033[2m", "\033[0m") if TTY else ("", "", "", "")


def outcome(proc: subprocess.CompletedProcess) -> Tuple[str, str]:
    if proc.returncode == 2:
        return "block", proc.stderr.strip()
    out = proc.stdout.strip()
    if not out:
        return "pass", ""
    try:
        data = json.loads(out.splitlines()[-1])
    except json.JSONDecodeError:
        return "pass", out[:120]
    hso = data.get("hookSpecificOutput") or {}
    if hso.get("permissionDecision"):
        return hso["permissionDecision"], hso.get("permissionDecisionReason", "")
    if data.get("decision") == "block":
        return "block", data.get("reason", "")
    return "pass", data.get("systemMessage", "")


def run_case(case: Dict[str, Any]) -> Tuple[bool, str, str]:
    hook = APP / ".claude" / "hooks" / case["hook"]
    if not hook.exists():
        return False, "missing", f"{hook.relative_to(ROOT)} not found"
    created: List[Path] = []
    for rel, content in (case.get("files") or {}).items():
        p = APP / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        created.append(p)
    event = dict(case["event"])
    event.setdefault("cwd", str(APP))
    event.setdefault("session_id", case.get("session", "hooktest"))
    for key in ("file_path",):
        ti = event.get("tool_input") or {}
        if key in ti and not str(ti[key]).startswith("/"):
            ti[key] = str(APP / ti[key])
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(APP)}
    try:
        proc = subprocess.run([sys.executable, str(hook)], input=json.dumps(event), cwd=APP,
                              capture_output=True, text=True, env=env, timeout=case.get("timeout", 180))
        got, detail = outcome(proc)
    finally:
        if case.get("cleanup", True):
            for p in created:
                p.unlink(missing_ok=True)
    return got == case["expect"], got, detail


def run_suite(name: str) -> Tuple[int, int]:
    spec = json.loads((SUITES / f"{name}.json").read_text())
    print(f"\n== hook test: {name} · {spec.get('title', '')}")
    for st in spec.get("reset_state", []):
        (APP / st).unlink(missing_ok=True)
    ok = 0
    for case in spec["cases"]:
        passed, got, detail = run_case(case)
        ok += passed
        mark = f"{G}PASS{X}" if passed else f"{R}FAIL{X}"
        print(f"   {mark}  {case['name']:<58} {D}expect {case['expect']:<5} got {got}{X}")
        if not passed and detail:
            print(f"         {D}↳ {detail[:150]}{X}")
    for st in spec.get("reset_state", []):
        (APP / st).unlink(missing_ok=True)
    verdict = f"{G}GREEN{X}" if ok == len(spec["cases"]) else f"{R}RED ({len(spec['cases']) - ok} failing){X}"
    print(f"   => {verdict}")
    return ok, len(spec["cases"])


def main() -> int:
    names = sys.argv[1:] or ["all"]
    if names == ["all"]:
        names = sorted(p.stem for p in SUITES.glob("*.json"))
    total_ok = total = 0
    for n in names:
        if not (SUITES / f"{n}.json").exists():
            print(f"no suite '{n}' (have: {', '.join(sorted(p.stem for p in SUITES.glob('*.json')))})")
            return 1
        ok, cnt = run_suite(n)
        total_ok += ok
        total += cnt
    print()
    return 0 if total_ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
