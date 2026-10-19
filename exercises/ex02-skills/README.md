# 🛠️ Exercise 2 · Skills: package the procedure, prove it fires

> ⏱️ **25 min** (timer presets 20 / 25 / 30) · 📅 Day 1, after the Skills deck (Fundamentals §16–17)
>
> 🧱 Builds on Ex 1 (`tools/start.sh` keeps your CLAUDE.md and rules) · 👉 **Students open [`exercise.html`](exercise.html)**

![A skill is a procedure that loads only when it's needed](img/skills.png)

---

## 🎯 Goal

**The drift:** ask for "the PR note for LED-105" and you get a plausible, generic note. Wrong
headings, no ADRs, and it says "lint passes" without ever running lint.

**The purpose:** a CLAUDE.md is always loaded, so it's the wrong place for a 40-line procedure. A
**skill** packages a procedure that loads only when it's needed. But a skill is only worth having if
it **fires** when it should, **stays quiet** when it shouldn't, and does **better than no skill**.

**By the end, students can:**

- ✍️ write a skill with every option from the lecture: `description`, `when_to_use`,
  `argument-hint`, scoped `allowed-tools`, `!`cmd`` dynamic context, `${CLAUDE_SKILL_DIR}` scripts,
  progressive disclosure with `reference.md`;
- 🎯 prove it fires by name, fires implicitly, and stays quiet on an unrelated question;
- 🍴 build a forked, read-only worker skill (`context: fork`, `agent`, `model`, `effort`);
- 📊 evaluate a skill like a feature: recall, false fires, quality with vs. without.

## 🧭 Where it fits

**Ex 1** made memory files work → **Ex 2** adds procedures on demand → leftover red: `allowed-tools`
limits the skill's own run, but the main session can still edit tests afterwards. A rule for every
agent needs a hook (**Ex 3**).

---

## 🗺️ The flow

| step | what happens | checked by | ⏱️ |
|---|---|---|---|
| 0 · 🔴 **No skill** | LED-120: "write the PR note for LED-105". A plausible, generic note | `tools/check.sh led-120` → **RED ×3** (house sections, ADRs touched, honest verification) | 4 |
| 1 · ✍️ **Author** | `ship-check`: SKILL.md + `reference.md` (template, path → ADR map) + `scripts/gates.py` | `skill_lint.py ship-check --profile ship-check` (18 static checks) | 7 |
| 2 · 🎯 **By name** | `/ship-check LED-105` | `check.sh led-120` → **GREEN** | 3 |
| 3 · 🪄 **Implicit** | (A) "make it reviewable", without naming the skill → must fire. (B) a plain question → must **not** fire | `check.sh trigger-implicit` · `check.sh trigger-quiet` | 5 |
| 4 · 🍴 **Worker** | `adr-audit`: read-only tools, `context: fork`, `agent: Explore`, `model: haiku`, `effort: low`. Compare `/context` with and without the fork | `skill_lint.py adr-audit --profile adr-audit` + the `/context` table | 6 |
| 5 · 📊 **Evaluate** (homework) | 4 prompts that should fire, 3 that shouldn't, × 3 runs, plus a no-skill **baseline** | `skill_eval.py … --runs 3 --baseline` → recall, false fires, quality, verdict | — |

✨ **Stretch:** install Superpowers and compare its reviewer; put `disable-model-invocation: true` on
a side-effect skill and confirm `trigger-quiet` never fires it.

---

## ⚖️ How it's judged

**🔍 The PR-note judge** (`drills/led-120-pr-note/probe_*.py`) checks:

- the six house headings are there;
- ADR-0001 and ADR-0002 are listed;
- **every gate claim matches a re-run** (a note saying "lint passes" when it doesn't is red);
- no code changed while writing it.

**🪄 Trigger checks** read the transcript for a `Skill` tool call naming the skill.

**📊 The eval** (`tools/skill_eval.py`, Step 5):

```bash
python3 tools/skill_eval.py exercises/ex02-skills/evals/ship-check.json --runs 3 --baseline
```

For every prompt × run, it does reset → apply your skills → `claude -p` → "did it fire?" → the
quality judge. The baseline repeats the should-fire prompts with the skill folder removed. The
report goes to `runs/skill-eval/ship-check/report.md`:

| metric | meaning | target |
|---|---|---|
| recall | should-fire prompts that fired | high |
| false fires | should-not-fire prompts that fired | 0 |
| quality with / without | judge passes with the skill vs. the baseline | with ≫ without |
| verdict | **ship it ✅** or **sharpen it 🔁** | |

### 🧩 Every lecture option has a check

| option (Skills deck) | step | how it's verified |
|---|---|---|
| description: what + when, third person | 1, 3 | linter (12+ words, third person, trigger conditions) + implicit/quiet drills |
| `when_to_use` | 1, 3 | linter (3+ phrasings) + `trigger-implicit` |
| `argument-hint` | 1, 2 | linter + visible in the `/` picker |
| `allowed-tools` as a sandbox | 1, 4 | linter (no bare Bash; read-only profile has no Edit) + a "fix it" attempt |
| `!`command`` dynamic context | 1 | linter + the gate table appears in the note |
| `${CLAUDE_SKILL_DIR}`: scripts run, not loaded | 1 | linter + the script runs from any cwd |
| progressive disclosure (`reference.md`) | 1 | linter (exists, and the body points to it) |
| `context: fork` · `agent` · `model` · `effort` | 4 | linter + `/context` before/after |
| "three should fire, one shouldn't" | 3, 5 | `trigger-implicit` + `trigger-quiet`; the full eval set in Step 5 |
| "baseline with vs. without before you trust it" | 5 | `skill_eval.py --baseline` |
| troubleshooting (YAML fences, tabs, name = folder, linked files) | 1 | linter generic checks |

---

## 📂 This folder

```
ex02-skills/
├── exercise.html            the student page (6 steps)
├── README.md · LESSONS.md
├── img/                     the diagram at the top
├── starter/gates.py         copied into the skill's scripts/ in Step 1
├── evals/ship-check.json    Step 5: should-fire / shouldn't-fire prompts
├── drills/
│   ├── led-120-pr-note/     Steps 0, 2 · prompt · setup.sh (applies LED-105) · the PR-note judge
│   ├── trigger-implicit/    Step 3A · same judge + "did the Skill tool fire?"
│   └── trigger-quiet/       Step 3B · "did everything stay quiet?"
└── reference/.claude/skills/   🔓 the answer
    ├── ship-check/          SKILL.md · reference.md · scripts/gates.py
    └── adr-audit/           SKILL.md
```

---

## 🧑‍🏫 Before class

1. `tools/doctor.sh`.
2. Record rates (implicit firing especially is probabilistic):
   ```bash
   tools/run_drill.sh led-120 none 3
   tools/run_drill.sh trigger-implicit exercises/ex02-skills/reference 3
   tools/run_drill.sh trigger-quiet exercises/ex02-skills/reference 3
   ```
3. Optional: numbers to show for Step 5:
   `python3 tools/skill_eval.py exercises/ex02-skills/evals/ship-check.json --variant exercises/ex02-skills/reference --runs 3 --baseline`
4. 🎭 Fallbacks: `tools/demo_reference.sh led-120 red|green`, `… trigger-implicit red|green`,
   `… trigger-quiet red|green` (hand-written reproductions, not recordings).

## 💬 Facilitator notes

- 👀 **Step 0's note looks good.** That's the point: ask what a reviewer would still have to chase
  (which ADRs? were lint and import-linter run?).
- 🧹 **The gate script is linted too.** It lives in `ledgerly/.claude/skills/`, so `ruff check .`
  covers it. Skills are code: review them in PRs.
- 📊 **Step 3 is a rate, not a pass.** Show the 3-run numbers you recorded.
- 🌉 **Step 4, hint 2 is the bridge to Ex 3.** `allowed-tools` limits the skill's own run; "never
  edit tests/" for every agent is a hook.

## 🖱️ Cursor sidebar

Cursor supports the Agent Skills standard (`SKILL.md` folders); check your version for which
frontmatter fields it honours. `context: fork`, `agent`, `model` and `effort` are Claude Code
fields. The linter's generic checks apply to both.

## 📝 Lessons

See [`LESSONS.md`](LESSONS.md). **Next:** [Ex 3 · Hooks](../ex03-hooks/).
