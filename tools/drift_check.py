#!/usr/bin/env python3
"""Drift checker: the "test runner" for agent behaviour.

Reads a drill's checks.json and verifies what the agent did (transcript) and what it left
behind (git diff vs the `baseline` tag, test/lint/arch commands, an HTTP probe).

    python3 tools/drift_check.py exercises/ex01-claude-md/drills/led-105-revenue --transcript latest   (or: tools/check.sh led-105)
    python3 tools/drift_check.py exercises/ex01-claude-md/drills/led-105-revenue --transcript runs/.../run-1.jsonl --label mine
    python3 tools/drift_check.py --summary runs/led-105-revenue

Exit code 0 = all checks passed, 1 = at least one failed.
(Hold on to that exit code: in Exercise 5 this script becomes a Stop hook.)

Standard library only, Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APP = ROOT / "ledgerly"
RUNS = ROOT / "runs"

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    GREEN = RED = YELLOW = DIM = RESET = ""


# --------------------------------------------------------------------------- transcript


class Transcript:
    """Tool calls, bash commands and metrics pulled from a Claude Code JSONL transcript.

    Works for both `claude -p --output-format stream-json` output and the session files
    Claude Code writes under ~/.claude/projects/ during interactive use.
    """

    def __init__(self, path: Optional[Path]):
        self.path = path
        self.tool_uses: List[Dict[str, Any]] = []
        self.assistant_texts: List[str] = []
        self.result: Dict[str, Any] = {}
        if path is None:
            return
        seen = set()
        for line in path.read_text(errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") == "result":
                self.result = obj
            for node in _walk(obj):
                if node.get("type") == "tool_use" and isinstance(node.get("input"), dict):
                    key = node.get("id") or json.dumps(node, sort_keys=True)
                    if key not in seen:
                        seen.add(key)
                        self.tool_uses.append(node)
            msg = obj.get("message") if isinstance(obj.get("message"), dict) else None
            if obj.get("type") == "assistant" and msg:
                for block in msg.get("content") or []:
                    if isinstance(block, dict) and block.get("type") == "text":
                        self.assistant_texts.append(block.get("text", ""))

    @property
    def available(self) -> bool:
        return self.path is not None

    @property
    def bash_commands(self) -> List[str]:
        return [str(t["input"].get("command", "")) for t in self.tool_uses if t.get("name") == "Bash"]

    @property
    def all_inputs(self) -> List[str]:
        return [f"{t.get('name')} {json.dumps(t.get('input'))}" for t in self.tool_uses]

    @property
    def final_message(self) -> str:
        if isinstance(self.result.get("result"), str):
            return str(self.result["result"])
        return self.assistant_texts[-1] if self.assistant_texts else ""

    def metrics(self) -> Dict[str, Any]:
        names = [t.get("name") for t in self.tool_uses]
        usage = self.result.get("usage") or {}
        tokens = None
        if usage:
            tokens = sum(
                int(usage.get(k) or 0)
                for k in (
                    "input_tokens",
                    "output_tokens",
                    "cache_read_input_tokens",
                    "cache_creation_input_tokens",
                )
            )
        return {
            "tool_calls": len(names),
            "explore_calls": sum(1 for n in names if n in ("Read", "Grep", "Glob", "LS")),
            "bash_calls": names.count("Bash"),
            "edits": sum(1 for n in names if n in ("Edit", "Write", "MultiEdit")),
            "turns": self.result.get("num_turns"),
            "tokens": tokens,
            "cost_usd": self.result.get("total_cost_usd"),
        }


def _walk(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def latest_transcript(app: Path) -> Optional[Path]:
    """Newest interactive session file for this project under ~/.claude/projects/."""
    base = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "projects"
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(app.resolve()))
    candidates = list((base / slug).glob("*.jsonl")) if (base / slug).is_dir() else []
    if not candidates:
        candidates = [p for p in base.glob("*ledgerly*/*.jsonl")]
    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


# --------------------------------------------------------------------------- repo state


def sh(cmd: str, cwd: Path, timeout: int = 300) -> Tuple[int, str]:
    proc = subprocess.run(
        cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout
    )
    return proc.returncode, (proc.stdout + proc.stderr)


# Memory/config files are the *treatment* the student adds, not the agent's change.
MEMORY_FILE = re.compile(
    r"(^|/)CLAUDE(\.local)?\.md$|^\.claude/|^\.mcp\.json$|^docs/(agent|standards)/"
)


def added_lines(app: Path, paths: List[str]) -> List[Tuple[str, str]]:
    """(file, line) for every line added since `baseline` under paths, incl. new files."""
    out: List[Tuple[str, str]] = []
    _, diff = sh("git diff baseline --unified=0 --no-color -- " + " ".join(paths), app)
    current = ""
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("+") and not line.startswith("+++") and not MEMORY_FILE.search(current):
            out.append((current, line[1:]))
    _, untracked = sh(
        "git ls-files --others --exclude-standard -- " + " ".join(paths), app
    )
    for rel in untracked.splitlines():
        if MEMORY_FILE.search(rel):
            continue
        p = app / rel
        if p.is_file() and p.suffix in (".py", ".sql", ".md", ".toml", ".json", ".cfg", ".txt"):
            out.extend((rel, ln) for ln in p.read_text(errors="replace").splitlines())
    return out


def changed_files(app: Path) -> List[str]:
    _, tracked = sh("git diff baseline --name-only", app)
    _, untracked = sh("git ls-files --others --exclude-standard", app)
    files = set(tracked.split()) | set(untracked.split())
    return sorted(f for f in files if not MEMORY_FILE.search(f))


# --------------------------------------------------------------------------- checks


def run_check(
    check: Dict[str, Any], app: Path, tr: Transcript, drill: Path
) -> Tuple[str, str]:
    """Returns (status, detail) where status is PASS / FAIL / SKIP."""
    kind = check["type"]
    flags = re.IGNORECASE

    if kind in ("transcript_absent", "transcript_present_all", "transcript_present_any"):
        if not tr.available:
            return "SKIP", "no transcript"
        haystack = tr.bash_commands if check.get("scope", "bash") == "bash" else tr.all_inputs
        hits = {p: [h for h in haystack if re.search(p, h, flags)] for p in check["patterns"]}
        if kind == "transcript_absent":
            found = {p: h for p, h in hits.items() if h}
            if found:
                p, h = next(iter(found.items()))
                return "FAIL", f"agent ran `{h[0][:90]}`"
            return "PASS", ""
        missing = [p for p, h in hits.items() if not h]
        if kind == "transcript_present_all":
            return ("FAIL", "never ran: " + ", ".join(missing)) if missing else ("PASS", "")
        return ("PASS", "") if len(missing) < len(hits) else ("FAIL", "none of the patterns ran")

    if kind == "final_message_matches":
        if not tr.available:
            return "SKIP", "no transcript"
        msg = tr.final_message
        ok = any(re.search(p, msg, flags) for p in check["patterns"])
        return ("PASS", "") if ok else ("FAIL", "final message: " + msg.strip()[:100])

    if kind == "command":
        code, out = sh(check["cmd"], app, timeout=check.get("timeout", 300))
        if code == check.get("expect_exit", 0):
            return "PASS", ""
        tail = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] or [""]
        return "FAIL", f"exit {code}: {tail[0][:100]}"

    if kind == "diff_absent":
        lines = added_lines(app, check.get("paths", ["src"]))
        for f, ln in lines:
            for p in check["patterns"]:
                if re.search(p, ln):
                    return "FAIL", f"{f}: {ln.strip()[:90]}"
        return "PASS", ""

    if kind == "diff_present":
        lines = added_lines(app, check.get("paths", ["tests"]))
        ok = any(re.search(p, ln) for _, ln in lines for p in check["patterns"])
        return ("PASS", "") if ok else ("FAIL", "expected change not found")

    if kind == "diff_no_removals":
        _, diff = sh("git diff baseline --unified=0 --no-color -- " + " ".join(check["paths"]), app)
        removed = [
            ln[1:].strip() for ln in diff.splitlines() if ln.startswith("-") and not ln.startswith("---")
        ]
        removed = [r for r in removed if r]
        return ("FAIL", f"removed/changed: {removed[0][:90]}") if removed else ("PASS", "")

    if kind == "files_unchanged":
        code, out = sh("git diff baseline --name-only -- " + " ".join(check["paths"]), app)
        changed = out.split()
        return ("FAIL", "modified: " + ", ".join(changed)) if changed else ("PASS", "")

    if kind == "probe":
        script = (drill / check["script"]).resolve()
        code, out = sh(f'uv run --quiet python "{script}"', app, timeout=120)
        msg = out.strip().splitlines()[-1] if out.strip() else ""
        return ("PASS", msg if code == 0 else "") if code == 0 else ("FAIL", msg[:110])

    return "SKIP", f"unknown check type {kind}"


# --------------------------------------------------------------------------- main


def check_drill(args: argparse.Namespace) -> int:
    drill = Path(args.drill).resolve()
    app = Path(args.app).resolve()
    spec = json.loads((drill / "checks.json").read_text())

    tpath: Optional[Path]
    if args.transcript in (None, "none"):
        tpath = None
    elif args.transcript == "latest":
        tpath = latest_transcript(app)
        if tpath is None:
            print(f"{YELLOW}No interactive transcript found; transcript checks skipped.{RESET}")
    else:
        tpath = Path(args.transcript)
    tr = Transcript(tpath)

    title = spec.get("title", drill.name)
    print(f"\n== Drift check: {title}  [{args.label}]")
    if tpath:
        print(f"{DIM}   transcript: {tpath}{RESET}")

    results = []
    for check in spec["checks"]:
        status, detail = run_check(check, app, tr, drill)
        colour = {"PASS": GREEN, "FAIL": RED}.get(status, YELLOW)
        print(f"   {colour}{status:4}{RESET}  {check['id']:<28} {DIM}{detail}{RESET}")
        if status == "FAIL" and check.get("why"):
            print(f"         {DIM}↳ {check['why']}{RESET}")
        results.append({"id": check["id"], "status": status, "detail": detail})

    metrics = tr.metrics() if tr.available else {}
    metrics["files_changed"] = len(changed_files(app))
    print("   " + DIM + "  ".join(f"{k}={v}" for k, v in metrics.items() if v is not None) + RESET)

    failed = sum(r["status"] == "FAIL" for r in results)
    verdict = f"{RED}RED ({failed} failing){RESET}" if failed else f"{GREEN}GREEN{RESET}"
    print(f"   => {verdict}\n")

    out_dir = Path(args.out) / drill.name
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "results.jsonl").open("a") as fh:
        fh.write(
            json.dumps(
                {
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "label": args.label,
                    "transcript": str(tpath) if tpath else None,
                    "results": results,
                    "metrics": metrics,
                }
            )
            + "\n"
        )
    return 1 if failed else 0


def summary(path: Path) -> int:
    rows = [json.loads(ln) for ln in (path / "results.jsonl").read_text().splitlines() if ln]
    by_label: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        by_label.setdefault(r["label"], []).append(r)
    check_ids: List[str] = []
    for r in rows:
        for c in r["results"]:
            if c["id"] not in check_ids:
                check_ids.append(c["id"])
    labels = list(by_label)
    width = max(len(c) for c in check_ids + ["check"]) + 2
    print(f"\n== Summary: {path.name}  (passes / runs)\n")
    print("   " + "check".ljust(width) + "".join(lb[:14].ljust(16) for lb in labels))
    for cid in check_ids:
        cells = []
        for lb in labels:
            runs = [c for r in by_label[lb] for c in r["results"] if c["id"] == cid]
            graded = [c for c in runs if c["status"] != "SKIP"]
            if not graded:
                cells.append("skip".ljust(16))
                continue
            p = sum(c["status"] == "PASS" for c in graded)
            colour = GREEN if p == len(graded) else (RED if p == 0 else YELLOW)
            cells.append(f"{colour}{p}/{len(graded)}{RESET}".ljust(16 + len(colour) + len(RESET)))
        print("   " + cid.ljust(width) + "".join(cells))
    for metric in ("tool_calls", "explore_calls", "tokens", "cost_usd", "files_changed"):
        cells = []
        for lb in labels:
            vals = [r["metrics"].get(metric) for r in by_label[lb]]
            vals = [v for v in vals if isinstance(v, (int, float))]
            avg = sum(vals) / len(vals) if vals else None
            if avg is None:
                cells.append("-".ljust(16))
            elif metric == "cost_usd":
                cells.append(f"${avg:.2f}".ljust(16))
            else:
                cells.append(f"{avg:,.0f}".ljust(16))
        print("   " + DIM + ("avg " + metric).ljust(width) + "".join(cells) + RESET)
    print()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("drill", nargs="?", help="exercise drill folder containing checks.json")
    ap.add_argument("--app", default=str(DEFAULT_APP))
    ap.add_argument("--transcript", default="latest", help="path | latest | none")
    ap.add_argument("--label", default="manual", help="variant name, e.g. none / good")
    ap.add_argument("--out", default=str(RUNS))
    ap.add_argument("--summary", metavar="RUN_DIR", help="print pass rates per variant")
    args = ap.parse_args()
    if args.summary:
        return summary(Path(args.summary))
    if not args.drill:
        ap.error("drill folder is required")
    return check_drill(args)


if __name__ == "__main__":
    sys.exit(main())
