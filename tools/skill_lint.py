#!/usr/bin/env python3
"""Static checks for a Claude Code skill, from the Skills lecture.

    python3 tools/skill_lint.py ship-check              # generic checks only
    python3 tools/skill_lint.py ship-check --profile ship-check
    python3 tools/skill_lint.py adr-audit  --profile adr-audit

Generic checks come from "It didn't fire · troubleshooting" and "Best practices": folder,
YAML fences, name = folder, a description that says what *and* when, linked files exist,
under 500 lines. Profiles add the advanced fields each Ex 2 skill must use.

Standard library only (no PyYAML): frontmatter is parsed as simple `key: value` lines.
Exit 0 = all pass, 1 = something failed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ledgerly"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DYNAMIC_RE = re.compile(r"!`[^`]+`")

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


class Skill:
    def __init__(self, folder: Path):
        self.folder = folder
        self.path = folder / "SKILL.md"
        self.text = self.path.read_text(errors="replace") if self.path.exists() else ""
        self.lines = self.text.splitlines()
        self.fm_ok = False
        self.fm: Dict[str, str] = {}
        self.fm_raw = ""
        self.body = self.text
        self.has_tabs = False
        self._parse()

    def _parse(self) -> None:
        if not self.lines or self.lines[0].strip() != "---":
            return
        try:
            end = next(i for i in range(1, len(self.lines)) if self.lines[i].strip() == "---")
        except StopIteration:
            return
        fm_lines = self.lines[1:end]
        self.fm_raw = "\n".join(fm_lines)
        self.has_tabs = "\t" in self.fm_raw
        self.body = "\n".join(self.lines[end + 1 :])
        key: Optional[str] = None
        for ln in fm_lines:
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", ln)
            if m and not ln.startswith((" ", "\t")):
                key = m.group(1)
                self.fm[key] = m.group(2).strip()
            elif key and ln.strip():
                self.fm[key] = (self.fm[key] + " " + ln.strip()).strip()
        for k, v in self.fm.items():
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                self.fm[k] = v[1:-1]
        self.fm_ok = True

    def tools(self, field: str = "allowed-tools") -> List[str]:
        raw = self.fm.get(field, "")
        raw = raw.strip("[]")
        # split on commas or whitespace that isn't inside parentheses
        parts, depth, cur = [], 0, ""
        for ch in raw:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if (ch == "," or ch.isspace()) and depth == 0:
                if cur.strip():
                    parts.append(cur.strip().strip("\"'"))
                cur = ""
            else:
                cur += ch
        if cur.strip():
            parts.append(cur.strip().strip("\"'"))
        return parts


Check = Tuple[str, Callable[[Skill], Optional[str]]]  # returns None on pass, reason on fail


def words(s: str) -> int:
    return len(re.findall(r"[A-Za-z']+", s))


GENERIC: List[Check] = [
    ("SKILL.md exists in .claude/skills/<name>/",
     lambda s: None if s.path.exists() else f"missing {s.path.relative_to(APP) if APP in s.path.parents else s.path}"),
    ("frontmatter fenced by --- … --- (first line exactly ---)",
     lambda s: None if s.fm_ok else "first line must be exactly --- and the block needs a closing ---"),
    ("no tabs in frontmatter (YAML wants spaces)",
     lambda s: "tab character found in frontmatter" if s.has_tabs else None),
    ("name: matches the folder, lowercase-hyphen",
     lambda s: None if s.fm.get("name") == s.folder.name and NAME_RE.match(s.fm.get("name", ""))
     else f"name is {s.fm.get('name')!r}, folder is {s.folder.name!r}"),
    ("description: says what it does (12+ words)",
     lambda s: None if words(s.fm.get("description", "")) >= 12
     else f"description has {words(s.fm.get('description', ''))} words: too vague to match against"),
    ("description: third person, not 'I…' / 'You…'",
     lambda s: "starts with I/You" if re.match(r"^(I|You)\b", s.fm.get("description", "")) else None),
    ("says WHEN to fire (when_to_use: or 'Use when' in description)",
     lambda s: None if s.fm.get("when_to_use") or re.search(r"\buse (it )?when\b", s.fm.get("description", ""), re.I)
     else "no trigger conditions: Claude only sees name + description before choosing"),
    ("body under 500 lines (push depth into reference files)",
     lambda s: None if len(s.body.splitlines()) < 500 else f"body is {len(s.body.splitlines())} lines"),
    ("every file the body links to exists",
     lambda s: _missing_links(s)),
]


def _missing_links(s: Skill) -> Optional[str]:
    refs = set(re.findall(r"\$\{CLAUDE_SKILL_DIR\}/([\w./-]+)", s.body))
    refs |= {m for m in re.findall(r"\(([\w./-]+\.(?:md|py|sh|json|txt))\)", s.body)}
    refs |= {m for m in re.findall(r"`([\w-]+\.md)`", s.body)}
    missing = [r for r in sorted(refs) if not (s.folder / r).exists()]
    return ("missing: " + ", ".join(missing)) if missing else None


def _phrasings(s: Skill) -> int:
    trig = s.fm.get("when_to_use", "") or s.fm.get("description", "")
    quoted = re.findall(r"[\"“']([^\"”']{3,})[\"”']", trig)
    return max(len(quoted), len([p for p in re.split(r"[,;]", trig) if words(p) >= 2]))


PROFILES: Dict[str, List[Check]] = {
    "ship-check": [
        ("when_to_use: lists 3+ phrasings people actually type",
         lambda s: None if s.fm.get("when_to_use") and _phrasings(s) >= 3
         else "add when_to_use with the real phrases: 'make this reviewable', 'PR description', …"),
        ("argument-hint: shows what to pass (e.g. <ticket-id>)",
         lambda s: None if s.fm.get("argument-hint") else "missing argument-hint"),
        ("allowed-tools: pre-approves what the skill runs (no prompts mid-skill)",
         lambda s: None if s.tools() else "missing allowed-tools: the gates script will stop for a permission prompt"),
        ("allowed-tools: Bash is scoped, never bare 'Bash'",
         lambda s: "bare Bash pre-approves ANY command; use Bash(uv run *), Bash(git diff *), …"
         if "Bash" in s.tools() else None),
        ("disallowed-tools: blocks Edit (writes the PR note, never edits code)",
         lambda s: None if "Edit" in s.tools("disallowed-tools")
         else "allowed-tools only pre-approves; to forbid editing code, add disallowed-tools: Edit"),
        ("arguments: if declared, every name is used as $name in the body (Step 6d)",
         lambda s: _named_args(s)),
        ("dynamic context: at least one !`command` line",
         lambda s: None if DYNAMIC_RE.search(s.body) else "no !`…` line: the skill arrives empty instead of pre-filled"),
        ("script referenced via ${CLAUDE_SKILL_DIR}/scripts/…",
         lambda s: None if re.search(r"\$\{CLAUDE_SKILL_DIR\}/scripts/", s.body)
         else "reference the script as ${CLAUDE_SKILL_DIR}/scripts/<file> so it resolves anywhere"),
        ("scripts/ has a script (run, not loaded)",
         lambda s: None if any((s.folder / "scripts").glob("*")) else "no file in scripts/"),
        ("reference.md exists and the body points to it (progressive disclosure)",
         lambda s: None if (s.folder / "reference.md").exists() and "reference.md" in s.body
         else "put the PR template in reference.md and tell the body to read it"),
    ],
    "adr-audit": [
        ("context: fork (own window, only the findings come back)",
         lambda s: None if s.fm.get("context") == "fork" else f"context is {s.fm.get('context')!r}, want fork"),
        ("agent: set (hand it to a subagent, e.g. Explore)",
         lambda s: None if s.fm.get("agent") else "missing agent"),
        ("model: pinned to a cheap tier (haiku or sonnet)",
         lambda s: None if re.search(r"haiku|sonnet", s.fm.get("model", ""), re.I)
         else f"model is {s.fm.get('model')!r}: a read-only sweep doesn't need the top tier"),
        ("effort: low or medium",
         lambda s: None if s.fm.get("effort") in ("low", "medium") else f"effort is {s.fm.get('effort')!r}"),
        ("read-only: Write/Edit blocked (disallowed-tools, or a read-only agent)",
         lambda s: _readonly(s)),
        ("dynamic context: at least one !`command` line",
         lambda s: None if DYNAMIC_RE.search(s.body) else "pre-fill the diff with !`git diff …`"),
    ],
}


def _named_args(s: Skill) -> Optional[str]:
    names = [n for n in re.split(r"[\s,\[\]]+", s.fm.get("arguments", "")) if n]
    if not names:
        return None  # optional: the field is Step 6d; without it, Claude Code appends ARGUMENTS anyway
    unused = [n for n in names if f"${n}" not in s.body]
    return ("declared but never used: " + ", ".join("$" + n for n in unused)) if unused else None


def _readonly(s: Skill) -> Optional[str]:
    # allowed-tools only pre-approves; it never removes a tool. Blocking takes disallowed-tools
    # or an agent whose own tool list is read-only.
    granted = [t for t in s.tools() if t in ("Write", "Edit", "MultiEdit", "NotebookEdit", "Bash")]
    if granted:
        return "allowed-tools pre-approves " + ", ".join(granted) + ": an audit must not"
    blocked = set(s.tools("disallowed-tools"))
    if {"Write", "Edit"} <= blocked or s.fm.get("agent") in ("Explore", "Plan"):
        return None
    return "nothing blocks Write/Edit: allowed-tools doesn't forbid, add disallowed-tools: Write, Edit"


def lint(name: str, profile: Optional[str], app: Path = APP, quiet: bool = False) -> List[Tuple[str, Optional[str]]]:
    skill = Skill(app / ".claude" / "skills" / name)
    checks = GENERIC + (PROFILES.get(profile, []) if profile else [])
    results = []
    for label, fn in checks:
        try:
            reason = fn(skill)
        except Exception as exc:  # a malformed skill must report, not crash
            reason = f"check crashed: {exc}"
        results.append((label, reason))
        if not skill.path.exists() and label.startswith("SKILL.md"):
            break
    if not quiet:
        tty = sys.stdout.isatty()
        g, r, d, x = (GREEN, RED, DIM, RESET) if tty else ("", "", "", "")
        print(f"\n== skill lint: {name}" + (f"  [profile {profile}]" if profile else ""))
        for label, reason in results:
            print(f"   {g + 'PASS' + x if reason is None else r + 'FAIL' + x}  {label}")
            if reason:
                print(f"         {d}↳ {reason}{x}")
        bad = sum(r_ is not None for _, r_ in results)
        print(f"   => {r + f'RED ({bad} failing)' + x if bad else g + 'GREEN' + x}\n")
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("name", help="skill folder name under ledgerly/.claude/skills/")
    ap.add_argument("--profile", choices=sorted(PROFILES), help="extra checks for an Ex 2 skill")
    ap.add_argument("--app", default=str(APP))
    a = ap.parse_args()
    res = lint(a.name, a.profile, Path(a.app))
    return 1 if any(r is not None for _, r in res) else 0


if __name__ == "__main__":
    sys.exit(main())
