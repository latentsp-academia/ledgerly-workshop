# Gated AI SDLC: keeping coding agents from drifting

*Latent · AI Coding Agents workshop · hands-on companion to the Fundamentals & Advanced decks*

Coding agents don't fail loudly. They drift: they follow a stale README, reuse the legacy
helper, "fix" a test so it passes, declare done without running your gates. Each run looks fine
in isolation, and the tests are often green.

This workshop teaches students to **see drift, measure it, and close it**, one mechanism at a
time, on a sample codebase built to drift.

## The method: TDD for agent behavior

Every exercise is a **drill** (a fixed prompt) plus a **drift check** (a deterministic script
that grades what the agent did and left behind).

```
🔴 RED       run the drill without the mechanism → watch the drift check fail
🟢 GREEN     add exactly one mechanism → same drill → green
🔵 REFACTOR  make it smaller / better placed → still green, cheaper
→ LEFTOVER   the red this mechanism can't fix motivates the next exercise
```

Two rules hold throughout:

1. **Loaded ≠ obeyed.** Every cycle has a *load check* (did it enter the context?) and a
   *behavior check* (did it change what happened?).
2. **Measure in rates.** Agents are nondeterministic. A drill runs 3–5 times per variant, and
   "2/3" counts as a result. The course's through-line is moving rules from *advisory*
   (a rate) to *enforced* (always):

```
◀ DETERMINISTIC ─ hooks · permissions · settings ─── CLAUDE.md · rules · skills ─ ADVISORY ▶
```

## What we protect against

| drift | example in Ledgerly | first caught by |
|---|---|---|
| Wrong source of truth | trusts the 2021 README: `make test`, Flask, dollars | Ex 1 · CLAUDE.md |
| False "done" | stops after pytest; never runs ruff / import-linter | Ex 1 → Ex 5 Stop hook |
| Architecture | builds on float `legacy_fx`; API imports the DB | Ex 1 → import-linter gate |
| Convention / scope | team rule in one person's `~/.claude` | Ex 1 |
| Instruction decay | rule said in chat, gone next session | Ex 1 |
| Grader tampering | edits a test to make the suite pass | Ex 1 (measured) → Ex 3 hook |
| Outdated libraries | Pydantic v1 / deprecated FastAPI APIs from training data | Ex 7 · MCP (Context7) |
| Scope creep | touches 12 files for a 1-file ticket | Ex 5 scope fence |
| Security | reads `.env`, edits `generated/`, destructive migrations | Ex 3 PreToolUse |
| Spec drift | builds what it *thought* you meant | Lesson 2 · spec-kit |

## Repo map

```
ledgerly-workshop/
├── README.md            ← you are here
├── ledgerly/            ← the sample app (its own git repo, tag `baseline`). Open Claude Code HERE.
├── exercises/           ← one folder per exercise
│   └── ex01-claude-md/
│       ├── exercise.html  ← the student page: steps, prompts, hints, timer, reference
│       ├── README.md      ← facilitator notes + timing
│       ├── LESSONS.md     ← takeaways + a table for your own numbers
│       ├── drills/        ← tickets the agent runs + what the drift checker looks for
│       └── reference/     ← reference implementation as real files (mirrors ledgerly/)
├── tools/               ← drill runner, drift checker, observers
├── runs/                ← created by the tools: transcripts + results (git-ignored)
└── my-variants/         ← your saved CLAUDE.md attempts (tools/snapshot.sh)
```

**Why are the exercises outside the app?** Because the agent runs inside `ledgerly/` and reads
whatever it finds. Answer keys next to the code would leak into its context. Keeping the grader
where the doer can't see it is itself a lesson (LED-103, Ex 3).

## Setup (10 min, before class)

Requirements: [Claude Code](https://code.claude.com), [uv](https://docs.astral.sh/uv/), git,
python3. Optional: Cursor.

```bash
cd ledgerly
uv sync
uv run pytest -q            # 21 passed, 1 deselected
uv run ruff check . && uv run lint-imports
cd ..
tools/reset.sh              # puts ledgerly/ back to the `baseline` tag at any time
```

> ⚠️ `tools/reset.sh` deletes untracked files in `ledgerly/`, including your CLAUDE.md.
> Save attempts first with `tools/snapshot.sh <name>`.

## Ledgerly: the sample app and its landmines

An invoicing & refunds API: FastAPI, SQLite, integer-cent `Money`, three layers
(`api → services → repo`, enforced by import-linter), four ADRs. It works and its tests pass.
It also contains what real repos contain:

| landmine | where | used in |
|---|---|---|
| Stale README (Flask, Postgres, `make test`, decimal dollars) | `README.md` | Ex 1 (step 0), Ex 7 |
| Float-based legacy FX + a legacy report built on it | `payments/legacy_fx.py`, `services/reports.py` | Ex 1 (step 0) |
| Legacy route that bypasses the service layer | `api/routes_refunds.py` (+ an `ignore_imports` exception) | Ex 2 |
| No error convention in code (it lives in people's heads) | API errors | Ex 1 (step 6) |
| VAT rounding that surprises customers (by design, ADR-0004) | `services/tax.py` | Ex 1 close (LED-103), Ex 3 |
| Fake secrets, not git-ignored | `.env` | Ex 3 |
| Generated code: "DO NOT EDIT" | `generated/tracker_client.py` | Ex 3 |
| Applied, destructive migration | `migrations/003_drop_audit_log_old.sql` | Ex 3 |
| Lint & architecture config an agent could "relax" | `ruff.toml`, `.importlinter` | Ex 3, Ex 4 |
| Flaky test (~10%: random invoice numbers collide) | `tests/test_invoices.py` `-m landmine` | Ex 5, Lesson 2 |

## Tools

| command | what it does |
|---|---|
| `tools/reset.sh [--keep-memory]` | `ledgerly/` → `baseline`. `--keep-memory` undoes the agent's code but keeps your CLAUDE.md files |
| `tools/check.sh <drill>` | grade `ledgerly/` + your newest Claude Code session, e.g. `tools/check.sh led-105` |
| `tools/run_drill.sh <drill> <none\|current\|folder> [N]` | N × (reset → apply memory files → `claude -p` headless → drift check), then a pass-rate table |
| `tools/apply_variant.sh <folder>` | copy a set of memory files (e.g. `exercises/ex01-claude-md/reference`) into `ledgerly/` |
| `tools/snapshot.sh <name>` | save your memory files as `my-variants/<name>` |
| `python3 tools/drift_check.py --summary runs/<drill>` | pass rates per variant, plus avg tool calls / tokens / cost |
| `tools/observe.sh on\|tail\|off` | log every CLAUDE.md / rule load (`InstructionsLoaded` hook) to `runs/loads.log` |
| `python3 tools/memory_size.py [file]` | approximate token cost of memory files, following `@imports` |
| `tools/demo_reference.sh <drill> red\|green` | facilitator fallback: apply the hand-written reference patch and check it |

Drills can be named by prefix: `led-105` (revenue endpoint), `led-112` (404 errors), `led-103` (impossible VAT ticket).

`run_drill.sh` runs Claude Code headless with `--permission-mode acceptEdits` and an allowlist of
project commands (`uv run`, `git diff`, …). Everything else is denied. Set `MODEL=…` to pin a model.

## Exercise map

### Lesson 1: build the gates (Fundamentals decks)

| # | exercise | 🔴 red that opens it | status |
|---|---|---|---|
| 1 | [CLAUDE.md hierarchy](exercises/ex01-claude-md/) · [open the page](exercises/ex01-claude-md/exercise.html) | no memory → stale README, float legacy, false "done" (tests green); then project · directory · rules · @import · user-level trap. 35 min | ✅ ready |
| 2 | Rules (`.claude/rules/`, `paths:`) | the testing rule from Ex 1 loads every session; the refund rule spans `api/` + `services/`; LED-103 tampering rate | planned |
| 3 | Hooks I: `PreToolUse` fence | tests edited, `.env` read, `generated/` edited, migration rewritten → **rate becomes 0** | planned |
| 4 | Hooks II: `PostToolUse` feedback | style drift, float money caught at edit time, not review time | planned |
| 5 | Hooks III: `Stop` finish line + `SessionStart` | false "done", scope creep. **The drift checker becomes the Stop hook** | planned |
| 6 | Skills | procedures bloating CLAUDE.md; vague tickets (grill-me intake), `/ship-check` | planned |
| 7 | MCP (+ Context7) | outdated library APIs (Pydantic v1, `on_event`) caught by `pytest -W error::DeprecationWarning`; context cost of MCP schemas | planned |
| 8 | Capstone | re-run LED-105 + LED-103 on the fully gated repo; compare scorecards | planned |

### Lesson 2: process on top of the gates (Advanced decks)

| # | exercise | idea |
|---|---|---|
| 9 | Custom agents | explorer / implementer / independent reviewer; **only the test-writer agent may edit tests** (doer ≠ judge) |
| 10 | Spec-kit | constitution derived from Ex 1–5; specify → clarify → plan → tasks → `analyze` gates `implement` |
| 11 | ADRs at level 2 | enforce exactly one ADR, the one that broke in LED-103 (ADR-0004) |
| 12 | Evaluation | requirement IDs ↔ tagged tests, holdout tests in CI, LLM-judge agent hook, `/goal` with all six parts |
| 13 | Workflows | adversarial fan-out verification; the same gates in CI so they can't be bypassed locally |

## Cursor

Every exercise has a short **Cursor sidebar** mapping the mechanism (`AGENTS.md`,
`.cursor/rules/*.mdc`, `.cursor/hooks.json`, `.cursor/mcp.json`). The drift checker is
tool-agnostic: it grades the repo state and works with any agent. Only the transcript-based
checks need a Claude Code session file. Mechanism details differ between Cursor versions, so
check your version's docs.

## A note on honesty

Agents are nondeterministic, and a live demo can come back green when you wanted red. Don't fake
it: show the multi-run rate you recorded before class, or the clearly labelled hand-written
reference patch. "It worked this time" is exactly the kind of evidence this workshop teaches
people not to trust.
