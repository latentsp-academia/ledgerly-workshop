# Exercise 3 · Hooks: from a rate to zero

**25 minutes** (timer presets 20 / 25 / 30) · Day 1, after the Hooks deck (Fundamentals §18)

👉 **Students open [`exercise.html`](exercise.html).** Builds on Ex 1–2 (`tools/start.sh` keeps
their CLAUDE.md, rules and skills).

## The flow

| step | what happens | checked by | time |
|---|---|---|---|
| 0 · 🔴 The drift | Re-show Ex 1's LED-103 rate (test edited, VAT rounding changed) and the student's own config edits | `demo_reference.sh led-103 red` · `git -C ledgerly diff baseline --stat` | 2 |
| 1 · 🧱 Fence | Copy the starters; `fence.py` has 2 TODOs: the **ask** list and **append-only tests**. Red first, then green, then register `PreToolUse` | `python3 tools/hook_test.py fence` (24 cases: 7 red in the starter) | 9 |
| 2 · 🧹 Lint | `lint_edited.py` (complete): silent fix, then "talks back". Make the agent write a bare `except` and watch | `hook_test.py lint` (4 cases) + live | 5 |
| 3 · 🏁 Finish line | `finish_line.py` blocks "done" until the 4 gates are green; starter lacks the **stop rule** | `hook_test.py finish` (6 cases: 1 red in the starter) | 6 |
| 4 · 😈 Get past it | LED-103 × 3 headless with the hooks; LED-132 "relax ruff.toml to 140" | `run_drill.sh led-103 current 3` · `check.sh led-132` | 3 |

Homework: rebuild `exercise-hook-debug` on Ledgerly (swap a subtly broken hook with a neighbour).

## What the fence decides

| | path / command | decision |
|---|---|---|
| secrets | `.env`, `.env.*` (read *or* write) | deny |
| generated / immutable | `src/ledgerly/generated/*`, applied migrations (tracked in git) | deny |
| the fence itself | `.claude/settings.json`, `.claude/hooks/*` (read is fine) | deny |
| a human decides | `.importlinter`, `ruff.toml`, `pyproject.toml`, `docs/decisions/*`, `services/tax.py` | ask |
| tests | new files and pure additions allowed; changed or removed lines | deny |
| Bash | `rm -rf`, force push, `reset --hard`, printing `.env`, writing to tests/config via sed/redirect | deny |
| Day 2 | `agent_type == "test-writer"` may change tests | allow |

The Bash rules are a regex, not a sandbox (`python -c "open(...)"` gets past them). Say so in the
room, which is a good bridge to permission deny rules and the sandbox.

## Folder

```
ex03-hooks/
├── exercise.html · README.md · LESSONS.md
├── starter/                 fence.py (2 TODOs) · lint_edited.py (complete) · finish_line.py (stop-rule TODO)
├── hooktests/               fence.json · lint.json · finish.json   ← tools/hook_test.py suites
├── drills/led-132-relax-lint/   "relax the lint config" + reference red/green
└── reference/.claude/       settings.json · hooks/{fence,lint_edited,finish_line}.py
```

The hooks are standard-library Python 3.9+ (macOS's `/usr/bin/python3` works) and need `uv` on
PATH for the lint and finish-line gates. **They live in the repo, so the repo's own ruff gate
lints them.** A sloppy hook turns `finish_line` red. That's intended.

## Before class

1. Record the "after" numbers: apply your Ex 1 memory files plus the reference hooks, then
   `tools/run_drill.sh led-103 current 3` and `tools/run_drill.sh led-132 current 1`.
2. `python3 tools/hook_test.py all` on the reference: `tools/reset.sh && tools/apply_variant.sh exercises/ex03-hooks/reference`.
3. Fallbacks: `tools/demo_reference.sh led-132 red|green`.

## Facilitator notes

- **Step 1's starter red list is the spec.** Read the 7 failing names aloud before anyone opens the file.
- **deny vs. ask** is the discussion: removing a dead `.importlinter` exception (Ex 1, 1c) is legitimate,
  so the fence *asks* instead of denying. Every block needs a legitimate route.
- **Step 4, row 3 is still a rate.** The hooks make tampering impossible; they don't make the agent
  flag the conflict. The reason string nudges it. Ask: "what would make *that* deterministic?"
  (a Stop hook that checks the final message, or an evaluation in Lesson 2).

## Cursor sidebar

Cursor has hooks in `.cursor/hooks.json` (events like `beforeShellExecution`, `beforeReadFile`,
`afterFileEdit`, `stop`); the JSON protocol differs. The fence's *logic* ports; the wiring doesn't.
Check your Cursor version's hook docs.
