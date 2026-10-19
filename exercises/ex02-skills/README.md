# Exercise 2 · Skills: package the procedure, prove it fires

**25 minutes** (timer presets 20 / 25 / 30) · Day 1, after the Skills deck (Fundamentals §16–17)

👉 **Students open [`exercise.html`](exercise.html).** It builds on Exercise 1:
`tools/start.sh` keeps their CLAUDE.md and rules, and adds skills on top.

## The flow

| step | what happens | checked by | time |
|---|---|---|---|
| 0 · 🔴 No skill | LED-120: "write the PR note for LED-105". The agent writes a plausible generic note | `tools/check.sh led-120` → **RED ×3** (house sections, ADRs touched, honest verification) | 4 |
| 1 · ✍️ Author | `ship-check`: SKILL.md (description, `when_to_use`, `argument-hint`, scoped `allowed-tools`, `!`…`` dynamic context, `${CLAUDE_SKILL_DIR}` script) + `reference.md` (template, path → ADR map) | `skill_lint.py ship-check --profile ship-check` (18 static checks) | 7 |
| 2 · 🎯 By name | `/ship-check LED-105` | `check.sh led-120` → **GREEN** | 3 |
| 3 · 🪄 Implicit | (A) "make it reviewable", without naming the skill → must fire. (B) a plain question → must **not** fire | `check.sh trigger-implicit` (Skill call in transcript) · `check.sh trigger-quiet` | 5 |
| 4 · ⚙️ Worker | `adr-audit`: read-only `allowed-tools`, `context: fork`, `agent: Explore`, `model: haiku`, `effort: low`. Compare `/context` with and without fork; try "fix it" from inside | `skill_lint.py adr-audit --profile adr-audit` + the student's `/context` table | 6 |

| 5 · 📊 Evaluate (homework) | An eval set: 4 prompts that should fire, 3 that shouldn't, × 3 runs, plus a no-skill **baseline** | `python3 tools/skill_eval.py exercises/ex02-skills/evals/ship-check.json --runs 3 --baseline` → recall, false fires, quality with vs. without, verdict | — |

Stretch (from `exercise-skills` / `exercise-skills_c`): install Superpowers and compare its reviewer;
`disable-model-invocation: true` on a side-effect skill and confirm `trigger-quiet` never fires it.

## How each lecture option is checked

| option (Skills deck) | where | how it's verified |
|---|---|---|
| description: what + when, third person | Step 1, 3 | linter (12+ words, third person, trigger conditions) + implicit/quiet drills |
| `when_to_use` | Step 1, 3 | linter (3+ phrasings) + `trigger-implicit` |
| `argument-hint` | Step 1, 2 | linter + visible in the `/` picker |
| `allowed-tools` as a sandbox | Step 1, 4 | linter (no bare Bash, no Edit / read-only profile) + "fix it" attempt |
| `!`command`` dynamic context | Step 1 | linter + the gate table appears in the note |
| `${CLAUDE_SKILL_DIR}`, scripts run, not loaded | Step 1 | linter + the script runs from any cwd |
| progressive disclosure (`reference.md`) | Step 1 | linter (exists and the body points to it) |
| `context: fork` · `agent` · `model` · `effort` | Step 4 | linter + `/context` before/after |
| "three should fire, one shouldn't" | Step 3, 5 | `trigger-implicit` + `trigger-quiet`; the full eval set in Step 5 |
| "baseline with vs. without before you trust it" | Step 5 | `skill_eval.py --baseline`: quality with the skill vs. the skill folder removed |
| troubleshooting (YAML fences, tabs, name = folder, linked files) | Step 1 | linter generic checks |

## Folder

```
ex02-skills/
├── exercise.html          ← the student page
├── README.md              ← this file (facilitator)
├── LESSONS.md
├── starter/gates.py       ← copied into the skill's scripts/ in Step 1
├── evals/ship-check.json  ← Step 5: should-fire / shouldn't-fire prompts for skill_eval.py
├── drills/
│   ├── led-120-pr-note/     Steps 0, 2 · prompt, setup.sh (applies LED-105), the hidden PR-note judge
│   ├── trigger-implicit/    Step 3A · same judge + "did the Skill tool fire?"
│   └── trigger-quiet/       Step 3B · "did everything stay quiet?"
└── reference/.claude/skills/
    ├── ship-check/          SKILL.md · reference.md · scripts/gates.py
    └── adr-audit/           SKILL.md
```

The hidden judge for the PR note (`drills/led-120-pr-note/probe_*.py`) checks the six house
headings, that ADR-0001 and ADR-0002 are listed, that **every gate claim matches a re-run** (a
note saying "lint passes" when it doesn't is red), and that no code changed while writing it.

## Before class

1. From the workshop root: `uv --directory ledgerly sync`.
2. Record rates (they are probabilistic, especially implicit firing):
   ```bash
   tools/run_drill.sh led-120 none 3
   tools/run_drill.sh trigger-implicit exercises/ex02-skills/reference 3
   tools/run_drill.sh trigger-quiet exercises/ex02-skills/reference 3
   ```
3. Optional: run the full eval once on the reference so you have numbers to show:
   `python3 tools/skill_eval.py exercises/ex02-skills/evals/ship-check.json --variant exercises/ex02-skills/reference --runs 3 --baseline`.
4. Fallbacks: `tools/demo_reference.sh led-120 red|green`, `… trigger-implicit red|green`,
   `… trigger-quiet red|green` (hand-written reproductions, not recordings).

## Facilitator notes

- **Step 0's note looks good.** That's the point: ask the room what a reviewer would still have to
  chase (which ADRs? were lint and import-linter run?).
- **The gate script is linted too.** It lives in `ledgerly/.claude/skills/`, so `ruff check .` covers
  it. A sloppy script turns the gates red. That's a good moment: skills are code, review them in PRs.
- **Step 3 is a rate, not a pass.** Implicit firing depends on the model's reasoning over descriptions.
  Show the 3-run numbers you recorded.
- **Step 4, hint 2 is the bridge to Ex 3.** `allowed-tools` limits the skill's own run; the main
  session can still edit after the fork returns. "Never edit tests/" for every agent is a hook.

## Cursor sidebar

Cursor supports the Agent Skills standard (`SKILL.md` folders). Check your version for which
frontmatter fields it honours. `context: fork`, `agent`, `model` and `effort` are Claude Code
fields. The linter's generic checks apply to both.
