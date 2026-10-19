#!/usr/bin/env python3
"""Evaluate a skill like a feature: does it fire when it should, stay quiet when it shouldn't,
and does it make the output better than no skill at all?

    python3 tools/skill_eval.py exercises/ex02-skills/evals/ship-check.json --runs 3
    python3 tools/skill_eval.py exercises/ex02-skills/evals/ship-check.json --quick      # 1 run, 2 prompts
    python3 tools/skill_eval.py exercises/ex02-skills/evals/ship-check.json --baseline   # + runs WITHOUT the skill
    python3 tools/skill_eval.py --report runs/skill-eval/ship-check                      # re-print

The evals file lists prompts that should fire the skill and prompts that shouldn't.
Each prompt runs headless N times (reset → your memory files → drill setup → claude -p):

  trigger recall    should-fire runs where the Skill tool was called
  false fires       should-not-fire runs where it was called anyway
  output quality    should-fire runs that pass the quality drill's hidden judge
  baseline          the same should-fire prompts with the skill folder removed

"--variant current" (default) freezes the memory files you have in ledgerly/ right now.
Env: CLAUDE_BIN (default: claude), MODEL, MAX_TURNS. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ledgerly"
sys.path.insert(0, str(ROOT / "tools"))
from drift_check import Transcript  # noqa: E402

ALLOWED = [
    "Read", "Edit", "Write", "Glob", "Grep", "Skill",
    "Bash(uv run:*)", "Bash(uv sync:*)", "Bash(python:*)", "Bash(python3:*)",
    "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(ls:*)", "Bash(cat:*)",
]


def sh(args: List[str], **kw: Any) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, **kw)


def resolve_drill(name: str) -> Path:
    out = sh(["bash", "-c", f'source "{ROOT}/tools/_lib.sh" && resolve_drill "{name}"'])
    if out.returncode != 0:
        sys.exit(out.stderr.strip())
    return Path(out.stdout.strip())


def freeze_current(dest: Path) -> None:
    """Copy the memory files (untracked CLAUDE.md, .claude/…, docs/standards/…) out of ledgerly/."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    files = sh(["git", "-C", str(APP), "ls-files", "--others", "--exclude-standard"]).stdout.split()
    keep = re.compile(r"(^|/)CLAUDE\.md$|^\.claude/|^\.mcp\.json$|^docs/standards/")
    for f in files:
        if keep.search(f):
            (dest / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(APP / f, dest / f)
    local = APP / "CLAUDE.local.md"
    if local.exists():
        shutil.copy2(local, dest / "CLAUDE.local.md")


def fired(transcript: Path, skill: str) -> bool:
    t = Transcript(transcript)
    return any(t_.get("name") == "Skill" and skill in json.dumps(t_.get("input")) for t_ in t.tool_uses)


def one_run(prompt: str, files: Path, setup: Optional[Path], skill: str, without_skill: bool,
            out: Path) -> Path:
    sh([str(ROOT / "tools/reset.sh")])
    sh([str(ROOT / "tools/apply_variant.sh"), str(files)])
    if without_skill:
        shutil.rmtree(APP / ".claude" / "skills" / skill, ignore_errors=True)
    if setup and (setup / "setup.sh").exists():
        sh([str(setup / "setup.sh"), str(APP)])
    cmd = [os.environ.get("CLAUDE_BIN", "claude"), "-p", prompt, "--output-format", "stream-json",
           "--verbose", "--permission-mode", "acceptEdits",
           "--max-turns", os.environ.get("MAX_TURNS", "30")]
    if os.environ.get("MODEL"):
        cmd += ["--model", os.environ["MODEL"]]
    cmd += ["--allowedTools", *ALLOWED]
    with out.open("w") as fh:
        subprocess.run(cmd, cwd=APP, stdout=fh, stderr=subprocess.DEVNULL, text=True)
    return out


def quality_ok(drill: Path, transcript: Path, label: str) -> bool:
    r = sh([sys.executable, str(ROOT / "tools/drift_check.py"), str(drill), "--transcript", str(transcript),
            "--label", label, "--out", str(ROOT / "runs/skill-eval/_quality")],
           env={**os.environ, "NO_COLOR": "1"})
    return r.returncode == 0


def evaluate(a: argparse.Namespace) -> Path:
    spec = json.loads(Path(a.cases).read_text())
    skill = spec["skill"]
    out_dir = ROOT / "runs" / "skill-eval" / skill
    out_dir.mkdir(parents=True, exist_ok=True)
    setup = resolve_drill(spec["setup_drill"]) if spec.get("setup_drill") else None
    qdrill = resolve_drill(spec["quality_drill"]) if spec.get("quality_drill") else None

    if a.variant == "current":
        files = out_dir / "_files"
        freeze_current(files)
    else:
        files = Path(a.variant).resolve()
    if not (files / ".claude" / "skills" / skill / "SKILL.md").exists():
        sys.exit(f"no .claude/skills/{skill}/SKILL.md in {files}: write the skill first (Step 1)")

    should, shouldnt = spec["should_fire"], spec["should_not_fire"]
    if a.quick:
        should, shouldnt, a.runs = should[:1], shouldnt[:1], 1

    rows: List[Dict[str, Any]] = []
    plan = [("should", p, False) for p in should] + [("shouldnt", p, False) for p in shouldnt]
    if a.baseline:
        plan += [("baseline", p, True) for p in should]
    total = len(plan) * a.runs
    n = 0
    for kind, prompt, without in plan:
        for i in range(1, a.runs + 1):
            n += 1
            print(f"[{n}/{total}] {kind:<8} run {i}: {prompt[:70]}", flush=True)
            t = out_dir / f"{kind}-{len(rows):03d}.jsonl"
            one_run(prompt, files, setup, skill, without, t)
            row = {"kind": kind, "prompt": prompt, "run": i, "transcript": str(t), "fired": fired(t, skill)}
            if kind in ("should", "baseline") and qdrill:
                row["quality"] = quality_ok(qdrill, t, f"eval-{kind}")
            rows.append(row)
    sh([str(ROOT / "tools/reset.sh")])
    sh([str(ROOT / "tools/apply_variant.sh"), str(files)])  # leave your files as you had them
    (out_dir / "results.json").write_text(json.dumps(
        {"skill": skill, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "runs": a.runs, "rows": rows}, indent=2))
    return out_dir


def rate(xs: List[bool]) -> str:
    return f"{sum(xs)}/{len(xs)}" if xs else "–"


def pct(xs: List[bool]) -> str:
    return f"{100 * sum(xs) // len(xs)}%" if xs else "–"


def report(out_dir: Path) -> int:
    data = json.loads((out_dir / "results.json").read_text())
    rows, skill = data["rows"], data["skill"]
    lines = [f"# Skill eval · {skill} · {data['ts']} · {data['runs']} run(s) per prompt", "",
             "| kind | prompt | fired | quality |", "|---|---|---|---|"]
    for kind in ("should", "shouldnt", "baseline"):
        for p in dict.fromkeys(r["prompt"] for r in rows if r["kind"] == kind):
            rs = [r for r in rows if r["kind"] == kind and r["prompt"] == p]
            q = rate([r["quality"] for r in rs if "quality" in r]) if kind != "shouldnt" else "n/a"
            label = {"should": "✅ should fire", "shouldnt": "🚫 shouldn't", "baseline": "⚪ no skill"}[kind]
            lines.append(f"| {label} | {p[:80]} | {rate([r['fired'] for r in rs])} | {q} |")
    should = [r for r in rows if r["kind"] == "should"]
    shouldnt = [r for r in rows if r["kind"] == "shouldnt"]
    base = [r for r in rows if r["kind"] == "baseline"]
    recall = [r["fired"] for r in should]
    false_fire = [r["fired"] for r in shouldnt]
    q_with = [r["quality"] for r in should if "quality" in r]
    q_without = [r["quality"] for r in base if "quality" in r]
    lines += ["", "| metric | value | target |", "|---|---|---|",
              f"| trigger recall (fires when it should) | {rate(recall)} · {pct(recall)} | ≥ 80% |",
              f"| false fires (fires when it shouldn't) | {rate(false_fire)} · {pct(false_fire)} | 0% |",
              f"| output quality WITH the skill | {rate(q_with)} · {pct(q_with)} | ≥ 80% |"]
    if base:
        lines.append(f"| output quality WITHOUT it (baseline) | {rate(q_without)} · {pct(q_without)} | lower than with |")
    verdict_ok = (recall and sum(recall) / len(recall) >= 0.8 and not any(false_fire)
                  and (not q_with or sum(q_with) / len(q_with) >= 0.8))
    lines += ["", f"**Verdict: {'ship it ✅' if verdict_ok else 'sharpen it 🔁'}**", "",
              "Recall low → add the phrasings people use to description / when_to_use. "
              "False fires → narrow the description to the job. "
              "Quality low but it fires → fix the body, template or script. "
              "No gap vs. baseline → the skill isn't earning its tokens."]
    text = "\n".join(lines) + "\n"
    (out_dir / "report.md").write_text(text)
    print("\n" + text)
    print(f"saved {out_dir.relative_to(ROOT)}/report.md")
    return 0 if verdict_ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("cases", nargs="?", help="evals JSON (should_fire / should_not_fire prompts)")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--variant", default="current", help="current | folder mirroring ledgerly/")
    ap.add_argument("--baseline", action="store_true", help="also run should-fire prompts without the skill")
    ap.add_argument("--quick", action="store_true", help="1 run of 1 should + 1 shouldn't prompt")
    ap.add_argument("--report", metavar="DIR", help="re-print a saved report")
    a = ap.parse_args()
    if a.report:
        return report(Path(a.report))
    if not a.cases:
        ap.error("evals file required")
    return report(evaluate(a))


if __name__ == "__main__":
    sys.exit(main())
