# 📜 Exercise 1 · CLAUDE.md + rules: see the drift, then fix it

> ⏱️ **30–36 min** (timer presets 30 / 35 / 40) · 📅 Day 1, after the Memory & rules deck (Fundamentals: Context, CLAUDE.md, Anti-patterns)
>
> 🧱 Builds on Ex 0 · 👉 **Students open [`exercise.html`](exercise.html)**

![Where memory lives decides who gets it and when it loads](img/memory-hierarchy.png)

---

## 🎯 Goal

**The drift:** an agent with no memory files does a reasonable-looking ticket and the tests pass,
but it follows the 2021 README, reuses float-based legacy code, never runs lint or the architecture
check, and ignores a house style that nothing in the code shows.

**The purpose:** show that a good CLAUDE.md *changes behaviour*, and that *where* you put each
instruction decides who gets it and when it loads.

**By the end, students can:**

- 📜 write a short project CLAUDE.md that fixes measurable drift (≤ 40 lines);
- 📁 place rules at the right level: project, directory (lazy), `.claude/rules/`, `@import`;
- 👁️ prove what loaded (`/context`, `observe.sh`) and keep **loaded** apart from **obeyed**;
- 🪤 spot the user-level trap: `~/.claude/CLAUDE.md` is invisible to teammates;
- 🧩 explain why even a perfect CLAUDE.md still gives a *rate* (the cliffhanger for Ex 3).

## 🧭 Where it fits

**Ex 0** got everyone to green gates → **Ex 1** opens the first red: *no memory* →
leftover red: **LED-103**, where the agent still edits a test sometimes. A rule can't make that
zero; a hook can (**Ex 3**).

---

## 🗺️ The flow

| step | what happens | the red → green | ⏱️ |
|---|---|---|---|
| 0 · 🔴 **No memory** | LED-105 (revenue endpoint) with no CLAUDE.md. Tests pass | **RED ×4**: stale README commands, float legacy, no full verification, house style | 5 |
| 1 · 📜 **Project** | write `ledgerly/CLAUDE.md` (3+ sections, ≤ 40 lines). Same ticket | one red survives: `value-object-convention` | 6 |
| 2 · 📁 **Directory** | `src/ledgerly/payments/CLAUDE.md`; `/context` from `payments/` vs root; watch it load lazily in `runs/loads.log` | load check | 5 |
| 3 · 📏 **Rules** | `.claude/rules/value-objects.md` (`@dataclass(frozen=True, slots=True, kw_only=True)`, no dicts from services) + `testing.md`. Same ticket | **GREEN** | 7 |
| 4 · 🔗 **@import** | `docs/standards/api-conventions.md` imported from CLAUDE.md; `memory_size.py` shows imports load eagerly | token cost | 4 |
| 5 · 🔍 **Diagnose** | fresh sessions at root and in `payments/`; tick what `/context` lists | the student's table | 2 |
| 6 · 🪤 **User trap** | Dev A puts the problem+json convention in `~/.claude/CLAUDE.md`. Dev B runs LED-112 | **RED**, then move it back → green | 7 |

🎬 **Close (2 min):** `tools/demo_reference.sh led-103 red`: an impossible VAT ticket where the
agent edits a test to make the suite pass. Even a perfect CLAUDE.md gives a *rate* → Ex 3.

---

## ⚖️ How it's judged

| drill | what the checks look at |
|---|---|
| **LED-105** revenue | transcript: no stale commands, ran pytest + ruff + format + lint-imports · diff: no `legacy_fx` / float money · `probe.py` calls the endpoint · **`probe_conventions.py`**: the hidden house-style test (frozen + slots + kw_only, services never return dicts) |
| **LED-112** 404s | `probe_status.py` (404, not 500) · `probe_problem_json.py` (the error body follows the convention) |
| **LED-103** VAT (close) | existing tests intact · tax policy unchanged · flagged the conflict instead of "fixing" it |

> 💡 The convention test is graded from **outside** the repo, so the agent can't learn the house
> style from it. `kw_only` appears nowhere in Ledgerly, so a CLAUDE.md-only agent almost never adds
> it. Only a rule carries it.

---

## 📂 This folder

```
ex01-claude-md/
├── exercise.html        the student page (7 steps)
├── README.md            this file
├── LESSONS.md           takeaways + "your numbers"
├── img/                 the diagram at the top
├── drills/
│   ├── led-105-revenue/   Steps 0, 1, 3 · prompt · checks · probe.py · probe_conventions.py · reference red / step1 / green
│   ├── led-112-errors/    Step 6 · prompt · checks · probes · the user-level snippet
│   └── led-103-vat/       close · the impossible ticket (facilitator demo)
└── reference/           🔓 the answer, mirroring ledgerly/
    ├── CLAUDE.md
    ├── docs/standards/api-conventions.md
    ├── src/ledgerly/payments/CLAUDE.md
    ├── .claude/rules/value-objects.md     the house-style rule
    ├── .claude/rules/testing.md
    └── user-level-CLAUDE.md.example       never applied: it belongs in ~/.claude
```

---

## 🧑‍🏫 Before class

1. `tools/doctor.sh` (or `uv --directory ledgerly sync && uv --directory ledgerly run pytest -q`: expect 21 passed).
2. Move your own `~/.claude/CLAUDE.md` aside. It contaminates every demo (that's Step 6).
3. Record real rates so a lucky live run can't derail you:
   ```bash
   tools/run_drill.sh led-105 none 3
   tools/run_drill.sh led-105 exercises/ex01-claude-md/reference 3
   tools/run_drill.sh led-103 exercises/ex01-claude-md/reference 5
   python3 tools/drift_check.py --summary runs/led-105-revenue
   ```
4. 🎭 Fallbacks if a live run won't go red: `tools/demo_reference.sh led-105 red` (Step 0),
   `… led-105 step1` (CLAUDE.md only: one red left), `… led-105 green` (with the rule).
   These are hand-written reproductions, not recordings. Say so in the room.

## 💬 Facilitator notes

- 🔴 **Step 0 is the hook.** Put the RED table on screen and ask "would you approve this PR?" The
  tests are green. The drift is in what it reused and what it never ran.
- 🧪 **Step 3 is the TDD moment.** Ask: "what in *your* codebase is house style that nothing in the
  code shows?"
- 👁️ **Step 2:** the `observe.sh tail` line appearing mid-session is the "aha". Have one student share
  their screen.
- 👥 **Step 6 works best in real pairs.** Solo students simulate Dev B by moving their user file
  aside. Remind everyone to restore it (hint 3 has the commands).
- ✂️ Short on time? Cut Step 5. Its table can be done from memory of Steps 2–4.

## 🖱️ Cursor sidebar

Cursor reads `AGENTS.md` and `.cursor/rules/*.mdc` (with `globs:`). User rules live in Cursor
Settings, which is the same trap as `~/.claude/CLAUDE.md`. To share one source between tools, keep
the content in `AGENTS.md` and make `CLAUDE.md` a single line: `@AGENTS.md`.

## 📝 Lessons

See [`LESSONS.md`](LESSONS.md). **Next:** [Ex 2 · Skills](../ex02-skills/).
