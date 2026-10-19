# Ledgerly exercise plan: where each exercise goes, and how long

- **Day 1 is the harness:** an orientation (Ex 0), then every building block gets a Ledgerly
  exercise, in deck order: CLAUDE.md + rules → skills → hooks → MCP → tests.
- **Day 2 is process on top of it:** subagents, then spec-driven development.

Each exercise opens with a red the previous one couldn't fix. The drift checker grades every one.

## Day 1 · Working with an agent: building blocks (242 min)

| min | block | slides (Fundamentals PDF §) | exercise |
|---|---|---|---|
| 15 | Intro | 01–04 | |
| **10** | 🧪 **Ex 0 · Orientation** ✅ built (18 min full version; `tools/doctor.sh` as pre-work) | | `ex00-orientation/` (replaces the 8-min pre-flight) |
| 12 | Harness | 05–06, 09 | |
| 7 | Models | 07–08 | |
| 15 | Context engineering | 11 | |
| 10 | Memory & rules | 10, 14 | |
| **30** | 🧪 **Ex 1 · CLAUDE.md + rules** ✅ built | | `ex01-claude-md/` (30-min preset: Step 5 becomes a hint) |
| 12 | ☕ Break | | |
| 4 | Output styles | 13 | |
| 12 | Skills | 16–17 | |
| **25** | 🧪 **Ex 2 · Skills** ✅ built | | `ex02-skills/` |
| 8 | Hooks | 18 | |
| **25** | 🧪 **Ex 3 · Hooks** ✅ built | | `ex03-hooks/` |
| 6 | MCP | 19 | |
| **4** | 🧪 **Ex 4 · MCP + Context7** ✅ built (live demo; full version is homework) | | `ex04-mcp/` |
| 8 | Cost optimisation | 21–22 | |
| 10 | Testing with AI agents | 23 | |
| **25** | 🧪 **Ex 5 · Tests: green is not correct** ✅ built | | `ex05-tests/` |
| 4 | 🧯 Buffer · Q&A | | |

**Total: 242 min (4 h 02).** Hands-on: 119 min (49%). Before the break: 99 min (Daniel's target is about 90).
Running Ex 0's full 18-minute version in class makes the day 250 min; keep it as pre-work instead.
The buffer is only 4 min. If the day runs long, Ex 4 is the first to cut (it's already a demo), then Ex 2 Step 4 (6 min).

## Day 2 · Subagents & spec-driven development (240 min)

Same blocks as the current Day 2 agenda; the exercises move onto Ledgerly so day 1's gates carry over.

| min | block | exercise |
|---|---|---|
| 8 | Recap: the gated repo from Day 1 | |
| 18 | Subagents · agent teams · skills vs subagents | |
| **25** | 🧪 **Ex 6 · Subagents: doer ≠ judge** | `ex06-subagents/` (replaces `exercise-subagents-verifier`) |
| 10 | Parallel agents · worktrees | |
| **30** | 🧪 **Ex 7 · Parallel tickets in worktrees** | `ex07-parallel/` (or keep `exercise-parallel-agents`) |
| 12 | ☕ Break | |
| 18 | Planning-first · de-sloping | |
| **25** | 🧪 Plan in phases | keep `exercise-plan-in-phases` |
| 20 | Spec Kit & ADRs | |
| **40** | 🧪 **Ex 8 · Spec Kit capstone** | `ex08-spec-kit/` (replaces `exercise-spec-kit-chess`) |
| 12 | Code review & failure modes | |
| 10 | Large codebases | |
| 12 | 🧯 Buffer · Q&A | |

---

# Day 1 exercises

## Ex 0 · Orientation · 10 min in class (18 full) · ✅ built · `ex00-orientation/`

No red. `tools/doctor.sh` (machine + gates green) → a map of Ledgerly and one invoice through
`/docs` → four README landmines and where the truth lives → the anatomy of an exercise folder
(drills, checks, probes, reference patches, `reference/`, README, LESSONS) → the tools table and
one warm-up drill (LED-100 `GET /version`) through start → agent → check → reset.

## Ex 1 · CLAUDE.md + rules · 30 min · ✅ built

Project → directory → rules (hidden house-style test: `frozen + slots + kw_only`) → `@` import →
user-level trap. Ends on the LED-103 cliffhanger: even a perfect CLAUDE.md gives a *rate*.

## Ex 2 · Skills · 25 min · ✅ built

See `ex02-skills/README.md`. Step 0 red (generic PR note) → author `ship-check` (linted) → by name →
implicit **and** quiet triggers → `adr-audit` as a forked, read-only worker. Every lecture option
(`when_to_use`, `argument-hint`, `allowed-tools`, `!`cmd``, `${CLAUDE_SKILL_DIR}`, `reference.md`,
`context: fork`, `agent`, `model`, `effort`) has a check.

## Ex 3 · Hooks · 25 min · ✅ built · `ex03-hooks/`

Test the hooks with `python3 tools/hook_test.py` (34 cases; the starter goes red on 8).

From `exercise-hooks`. Opens on Ex 1's LED-103 rate and ends at **0/3 by construction**.

| step | what | min |
|---|---|---|
| 0 🔴 | Re-show the LED-103 tampering rate | 1 |
| 1 | `PreToolUse` fence: tests **append-only**; `.importlinter`, `ruff.toml`, `.env`, `generated/`, applied migrations protected. Test it with JSON on stdin **before** wiring it | 9 |
| 2 | `PostToolUse` ruff: silent fix, then "talks back" with exit 2 | 5 |
| 3 | `Stop` finish line: the drift checker *is* the hook (`stop_hook_active`, 3-attempt cap) | 6 |
| 4 😈 | Try to get past it: LED-103 ×3 → 0/3. Where's the legitimate route? (The hook's message says: flag the ADR conflict) | 4 |

Homework: `exercise-hook-debug` rebuilt on Ledgerly.

## Ex 4 · MCP + Context7 · 4 min demo (20 min homework) · ✅ built · `ex04-mcp/`

Red: LED-141 "seed demo data at startup" → agents often write FastAPI `@app.on_event`, deprecated
in the pinned FastAPI. Tests green; the hidden judge records DeprecationWarnings raised from
`src/ledgerly/`. Green: Context7 in `.mcp.json` + `.claude/rules/libraries.md` → `lifespan`.
Enforce: a human adds `filterwarnings = ["error::DeprecationWarning:ledgerly"]`. Cost: the MCP tools
line in `/context`. Homework: a local tracker MCP server for the tickets.

## Ex 5 · Tests: green is not correct · 25 min · ✅ built · `ex05-tests/`

From `exercise-testing-ai-generated-code` and `space-invaders-tdd`. Since Ex 3's hook fences the
tests, the question is no longer "will it cheat?" but "are the tests any good?"

| step | what | min |
|---|---|---|
| 0 🔴 | LED-150 weak ask on partial refunds (LED-101 pre-applied). A hidden judge plants 7 mutants, one per ADR-0003 rule, and runs only the new tests. Weak tests kill few | 6 |
| 1 | Keep/drop: rule-check, mirror of the code, or duplicate? | 5 |
| 2 | LED-151 contract ask from ADR-0003 (a rule per test, boundaries, don't change the code) → ≥ 6/7 killed | 9 |
| 3 🪤 | The trap: LED-118 "make the flaky test pass" with the Ex 3 hooks on. A `skip` line is an addition, so the append-only fence lets it through; the judge (30/30 runs, no skip, fix in code) catches it | 5 |

# Day 2 exercises

## Ex 6 · Subagents: doer ≠ judge · 25 min · `ex06-subagents/`

`.claude/agents/`: an `explorer` (haiku, read-only), an `implementer`, a `test-writer`, and an
independent `reviewer`. Extends the Ex 3 fence: **only `test-writer` may edit `tests/`** (the hook
checks `agent_type`). Red: the implementer's own tests let mutants survive (Ex 5's judge).
Green: the test-writer writes from the ADR, and the reviewer flags what the implementer missed.

## Ex 7 · Parallel tickets in worktrees · 30 min · `ex07-parallel/`

LED-101 (partial refunds) and LED-112 (404s) in two worktrees at once. The Day 1 gates run in
both; merge, re-run the drift checker on `main`.

## Ex 8 · Spec Kit capstone · 40 min · `ex08-spec-kit/`

LED-201 multi-currency refunds. Constitution generated from Ex 1's rules and the ADRs; `/analyze`
gates `/implement`; every FR-ID needs a `@pytest.mark.req("FR-00x")` test (the checker verifies);
holdout tests live in the drill folder, and an ADR-level check enforces ADR-0003.
