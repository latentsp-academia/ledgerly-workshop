# Exercise 1 · CLAUDE.md: see the drift, then fix it

**36 minutes** (timer presets 30 / 35 / 40) · Day 1 · Fundamentals deck: Context, CLAUDE.md,
Anti-patterns, Spine, Decide

👉 **Students open [`exercise.html`](exercise.html)** in a browser. It has every step, the
paste-ready prompts, the acceptance criteria, hints that unlock one level at a time, and a locked
reference implementation.

## The flow

| step | what happens | time |
|---|---|---|
| 0 · 🔴 No memory | Agent does LED-105 with no CLAUDE.md. Tests pass; the drift checker shows **RED ×4** (stale README commands, float legacy code, no full verification, house style). | 5 |
| 1 · 📜 Project | Write `ledgerly/CLAUDE.md` (3+ sections, ≤40 lines). Same ticket → **one red survives**: `value-object-convention`. | 6 |
| 2 · 📁 Directory | `src/ledgerly/payments/CLAUDE.md`. `/context` from `payments/` vs. root; watch it load lazily in `runs/loads.log`. | 5 |
| 3 · 📏 Rules | `.claude/rules/value-objects.md` (house style: `@dataclass(frozen=True, slots=True, kw_only=True)`, no dicts from services) + `testing.md`. Same ticket → **GREEN**. Stretch: `paths:` frontmatter. | 7 |
| 4 · 🔗 @ import | `docs/standards/api-conventions.md` imported from CLAUDE.md; `memory_size.py` shows imports load eagerly. | 4 |
| 5 · 🔍 Diagnose | Fresh sessions at root and in `payments/`; tick what `/context` lists. | 2 |
| 6 · 🪤 User trap | Dev A moves problem+json into `~/.claude/CLAUDE.md`. Dev B runs LED-112 → **RED**. Move it back → green. | 7 |

Close (facilitator, 2 min): `tools/demo_reference.sh led-103 red`. An impossible VAT ticket where the
agent edits a test to make the suite pass. Even a perfect CLAUDE.md gives a *rate*. That's the
cliffhanger for hooks (Ex 3).

## Folder

```
ex01-claude-md/
├── exercise.html        ← the student page
├── README.md            ← this file (facilitator)
├── LESSONS.md           ← takeaways
├── drills/              ← the tickets + what the checker looks for
│   ├── led-105-revenue/   Steps 0, 1, 3 · prompt, checks, probes (incl. the hidden convention test), reference red / step1 / green patches
│   ├── led-112-errors/    Step 6    · prompt, checks, probes, the user-level snippet
│   └── led-103-vat/       close     · the impossible ticket (facilitator demo)
└── reference/           ← the reference implementation, as real files mirroring ledgerly/
    ├── CLAUDE.md
    ├── docs/standards/api-conventions.md
    ├── src/ledgerly/payments/CLAUDE.md
    ├── .claude/rules/value-objects.md   (the house-style rule)
    ├── .claude/rules/testing.md
    └── user-level-CLAUDE.md.example   (never applied: it belongs in ~/.claude)
```

## Before class

1. From the workshop root: `uv --directory ledgerly sync && uv --directory ledgerly run pytest -q`
   (expect 21 passed).
2. Move your own `~/.claude/CLAUDE.md` aside. It contaminates every demo (that's Step 6).
3. Record real rates so a lucky live run can't derail you:
   ```bash
   tools/run_drill.sh led-105 none 3
   tools/run_drill.sh led-105 exercises/ex01-claude-md/reference 3
   tools/run_drill.sh led-103 exercises/ex01-claude-md/reference 5
   ```
   `python3 tools/drift_check.py --summary runs/led-105-revenue` re-prints the table any time.
4. Fallback if a live run won't go red: `tools/demo_reference.sh led-105 red` (Step 0),
   `… led-105 step1` (CLAUDE.md only: one red left), `… led-105 green` (with the rule). It's a
   hand-written reproduction, not a recording. Say so in the room.

## Facilitator notes

- **Step 0 is the hook.** Put the RED table on screen and ask "would you approve this PR?" The tests
  are green. The drift is in what it reused and what it never ran.
- **Step 3 is the TDD moment.** The convention test (`drills/led-105-revenue/probe_conventions.py`)
  is graded from *outside* the repo, so the agent can't learn the house style from it. `kw_only`
  appears nowhere in Ledgerly, so a CLAUDE.md-only agent almost never adds it, and the rule
  turns it green. Ask: "what in *your* codebase is house style that nothing in the code shows?"
- **Step 2:** the `observe.sh tail` line appearing mid-session is the "aha". Have one student share
  their screen.
- **Step 6 works best in real pairs.** Solo students simulate Dev B by moving their user file aside.
  Remind everyone to restore it (hint 3 has the commands).
- If you're short on time, cut Step 5. Its table can be done from memory of Steps 2–4.

## Cursor sidebar

Cursor reads `AGENTS.md` and `.cursor/rules/*.mdc` (with `globs:`). User rules live in Cursor
Settings, which is the same trap as `~/.claude/CLAUDE.md`. To share one source between tools, keep
the content in `AGENTS.md` and make `CLAUDE.md` a single line: `@AGENTS.md`.
