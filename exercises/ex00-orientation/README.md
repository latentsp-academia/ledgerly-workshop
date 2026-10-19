# Exercise 0 · Orientation: the app, the tools, the loop

**18 minutes** (or pre-work + a 10-minute version in class) · Day 1, right after the intro, before Ex 1

👉 **Students open [`exercise.html`](exercise.html).** This page is for the facilitator.

Ex 0 has no red to fix. Its job is to make sure that by Ex 1 every student:

- has green gates;
- knows Ledgerly well enough to judge an agent's changes to it;
- knows how an exercise folder is built (drills, checks, hidden judges, references, LESSONS);
- has run the start → agent → check → reset loop once.

## The flow

| step | what happens | checked by | time |
|---|---|---|---|
| 0 · 🩺 Doctor | `tools/doctor.sh`: claude, uv, git, python3; `baseline` tag; `uv sync`; pytest, ruff, import-linter; warns about `~/.claude/CLAUDE.md` | ends with **READY** | 2 |
| 1 · 🗺️ Ledgerly | Project map (layers, ADRs, landmine folders). Run it with uvicorn, then use `/docs` to create → capture → refund an invoice | open → paid → refunded | 4 |
| 2 · 💣 Landmines | Four README claims; students find where the truth lives (pyproject/uv.lock, app.py/db.py, ADR-0001, refunds.py) | answer key in the page's reference | 3 |
| 3 · 📁 Anatomy | Walk `exercises/ex00-orientation/`, then list Ex 1's `drills/` and `reference/` (names only). A table explains every part and which tool uses it | can explain prompt/checks/probe | 4 |
| 4 · 🔁 The loop | The tools table, then LED-100 `GET /version` with their own agent → `tools/check.sh led-100` → write the result in LESSONS.md → `tools/reset.sh` | a check report | 5 |

**10-minute in-class version:** Step 0 as pre-work. In class, show the Step 1 map (2 min), skim Step 3's
table (3 min), and run Step 4 (5 min). Steps 1 (tour) and 2 (landmines) can be homework.

## LED-100, the warm-up drill

`drills/led-100-version/`: "add `GET /version`" with the version from `pyproject.toml`.

| check | what it does |
|---|---|
| tests-pass | runs the test suite |
| lint-clean | runs ruff |
| endpoint-works | `probe.py` calls the endpoint itself |
| new-behaviour-tested | requires a change under `tests/` mentioning `/version` |

The ticket doesn't ask for a test, so a red on `new-behaviour-tested` is common and that's the hook
into Ex 1: *whose job was it to say "every change comes with a test"?* Either result is fine here.
Fallback: `tools/demo_reference.sh led-100 red|green`.

Ex 0 has no top-level `reference/` (there's no mechanism to install). Its reference section on the
page holds the landmine answer key and the folder anatomy.

## Before class

1. Send students the page and ask them to run `tools/doctor.sh` before they arrive.
2. Run `tools/doctor.sh` on the machine you present from.
3. Optional: `tools/run_drill.sh led-100 none 3` to have a rate to show for Step 4.

## Folder

```
ex00-orientation/
├── exercise.html · README.md · LESSONS.md
└── drills/led-100-version/   prompt · checks.json · probe.py · reference red/green
```

## Cursor sidebar

Steps 0–3 are tool-agnostic. For Step 4, open `ledgerly/` in Cursor, paste LED-100 into the agent and
run `tools/check.sh led-100`. All four checks grade the repo, so no Claude Code session is needed.
