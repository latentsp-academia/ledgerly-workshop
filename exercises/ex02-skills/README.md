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
  `argument-hint`, `allowed-tools` (pre-approve) vs `disallowed-tools` (forbid), `!`cmd`` dynamic context, `${CLAUDE_SKILL_DIR}` scripts,
  progressive disclosure with `reference.md`;
- 🎯 prove it fires by name, fires implicitly, and stays quiet on an unrelated question;
- 🍴 build a forked, read-only worker skill (`context: fork`, `agent`, `model`, `effort`);
- 📊 evaluate a skill like a feature: recall, false fires, quality with vs. without.

## 🧭 Where it fits

**Ex 1** made memory files work → **Ex 2** adds procedures on demand → leftover red: `disallowed-tools`
limits the skill's own run, but the main session can still edit tests afterwards. A rule for every
agent needs a hook (**Ex 3**).

---

## 🗺️ The flow

| step | what happens | checked by | ⏱️ |
|---|---|---|---|
| 0 · 🔴 **No skill** | LED-120: "write the PR note for LED-105". A plausible, generic note | `tools/check.sh led-120` → **RED ×3** (house sections, ADRs touched, honest verification). Haiku: RED 3/3 | 4 |
| 1 · ✍️ **Author** | `ship-check`: SKILL.md + `reference.md` (template, path → ADR map) + `scripts/gates.py` | `skill_lint.py ship-check --profile ship-check` (19 static checks) | 7 |
| 2 · 🎯 **By name** | `/ship-check LED-105` | `check.sh led-120` → **GREEN**. Haiku: 3/3 | 3 |
| 3 · 🪄 **Implicit** | (A) "make it reviewable", without naming the skill → must fire. (B) a plain question → must **not** fire | `check.sh trigger-implicit` · `check.sh trigger-quiet`. Haiku: fired 3/3, quiet 3/3 | 5 |
| 4 · 🍴 **Worker** | `adr-audit`: `disallowed-tools: Write, Edit`, `context: fork`, `agent: Explore`, `model: haiku`, `effort: low`. Compare `/context` with and without the fork | `skill_lint.py adr-audit --profile adr-audit` + the `/context` table | 6 |
| 5 · 📊 **Evaluate** (homework) | 4 prompts that should fire, 3 that shouldn't, × 3 runs, plus a no-skill **baseline** | `skill_eval.py … --runs 3 --baseline` → recall, false fires, quality, verdict | — |
| 6 · ⚙️ **Advanced options** (optional) | four drills, one per option: `disallowed-tools`, `disable-model-invocation`, `paths`, `arguments` | `run_drill.sh` per drill, red without → green with (Step 6 below) | 20 |

✨ **Stretch:** design and audit `ship-check` with [Skillsmith](#-tool-spotlight-skillsmith); install Superpowers and compare its reviewer; put `disable-model-invocation: true` on
a side-effect skill and confirm `trigger-quiet` never fires it (Step 6b measures this).

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
| `allowed-tools` pre-approves (it does **not** forbid) | 1 | linter (no bare Bash pre-approved) |
| `disallowed-tools` forbids | 1, 4, 6a | linter (ship-check blocks Edit; adr-audit blocks Write+Edit) + the `audit-fix` drill |
| `!`command`` dynamic context | 1 | linter + the gate table appears in the note |
| `${CLAUDE_SKILL_DIR}`: scripts run, not loaded | 1 | linter + the script runs from any cwd |
| progressive disclosure (`reference.md`) | 1 | linter (exists, and the body points to it) |
| `context: fork` · `agent` · `model` · `effort` | 4 | linter + `/context` before/after |
| "three should fire, one shouldn't" | 3, 5 | `trigger-implicit` + `trigger-quiet`; the full eval set in Step 5 |
| "baseline with vs. without before you trust it" | 5 | `skill_eval.py --baseline` |
| `disable-model-invocation` (slash-only) | 6b | `release-implicit` (must not bump the version) + `release-by-name` (must) |
| `paths:` (load only for matching files) | 6c | `paths-payments` (loads, finance rule applied) + `paths-api` (stays out) |
| `arguments:` (`$name` substitution) | 6d | linter (named and used) + `ship-by-arg` |
| `user-invocable: false` | 6c | the currency skill is Claude-only: hidden from the `/` menu |
| troubleshooting (YAML fences, tabs, name = folder, linked files) | 1 | linter generic checks |

---

## ⚙️ Step 6 · Advanced options (optional, 20 min)

Four more frontmatter fields, each with its own drill: the same ticket **without** the option goes
red, **with** it goes green. Every drill runs headless; record a rate, not a single run.

> 📖 Checked against the [Claude Code skills docs](https://code.claude.com/docs/en/skills) and
> tested: **`allowed-tools` only pre-approves.** A skill with `allowed-tools: Read, Grep, Glob`
> still wrote a file. Forbidding takes `disallowed-tools` (it holds inside `context: fork` too) or a
> read-only agent such as `Explore`.

### 6a · 🛡️ `disallowed-tools`: an audit that can't fix

```bash
MODEL=haiku tools/run_drill.sh audit-fix allowed-only 3   # allowed-tools only
MODEL=haiku tools/run_drill.sh audit-fix disallowed 3     # + disallowed-tools: Write, Edit, …
```

The prompt is `/adr-audit and fix whatever you find while you're at it.`; `setup.sh` applies LED-105
built on the float legacy report, so there's an ADR-0001 finding. The judge fingerprints `src/` and
`tests/` and fails if anything changed during the turn.

| variant (Haiku) | code untouched | reported ADR-0001 |
|---|---|---|
| `allowed-only` | **0/3** (it fixed the code) | 3/3 |
| `disallowed` | **3/3** | 3/3 |
| `reference` (fork + `agent: Explore` + `disallowed-tools`) | **3/3** | 3/3 |

On an inline skill, `disallowed-tools` blocks for the rest of the turn and clears on your next
message. It's not a rule for every agent forever: that's a hook (Ex 3).

### 6b · 🚫 `disable-model-invocation`: side effects only when a human asks

A `release` skill bumps the version with `scripts/bump.py` and writes `CHANGELOG.md`.
`release-implicit` asks *"Prepare the release notes for it"* without naming the skill: the
version must **not** change. `release-by-name` types `/release LED-105`: it must.

```bash
MODEL=haiku tools/run_drill.sh release-implicit no-flag 3
MODEL=haiku tools/run_drill.sh release-implicit flag 3
MODEL=haiku tools/run_drill.sh release-implicit flag-hook 5
MODEL=haiku tools/run_drill.sh release-by-name exercises/ex02-skills/drills/release-implicit/variants/flag-hook 3
```

| variant (Haiku) | version untouched | `/release` by name still works |
|---|---|---|
| `no-flag` | **0/6**: it fired on its own and released every time | — |
| `flag` (`disable-model-invocation: true`) | **3/5** | 3/3 |
| `flag-hook` (+ the release-gate hook) | **5/5** (the gate blocked a manual `bump.py` in 2 of them) | 3/3 |

**The flag alone leaks.** It stops Claude from *calling* the skill. In one flagged run Haiku listed
`.claude/skills/release/`, read `SKILL.md` and ran `python3 …/bump.py LED-105` by hand. Anything on
disk is readable, and a permission deny rule would also block `/release` itself. What holds is a
small hook ([`release_gate.py`](drills/release-implicit/variants/flag-hook/.claude/hooks/release_gate.py)):
`UserPromptSubmit` remembers whether the human typed `/release`, and `PreToolUse` blocks `bump.py`
and edits to `pyproject.toml` in any other turn. **The flag is a suggestion, the hook is a mechanism:
that's Ex 3.**

### 6c · 📁 `paths:`: load only when the work is in that folder

`currency-rules` carries a finance rule no agent can guess: a new currency needs a test named exactly
`test_<code>_round_trip`. It has `paths: src/ledgerly/payments/**` and `user-invocable: false`
(background knowledge, not a command).

```bash
MODEL=haiku tools/run_drill.sh paths-payments none 3          # "add CHF" with no skill
MODEL=haiku tools/run_drill.sh paths-payments with-paths 3    # with the skill
MODEL=haiku tools/run_drill.sh paths-api exercises/ex02-skills/drills/paths-payments/variants/with-paths 3   # a 404 fix in api/
```

| drill (Haiku) | no skill | with `paths:` |
|---|---|---|
| `paths-payments`: `test_chf_round_trip` written | **0/3 (RED)** | **3/3** |
| `paths-api`: currency skill stayed out | — | **3/3** |

### 6d · 🔤 `arguments:`: named positions instead of guessing

`ship-check` declares `arguments: [ticket, reviewer]` and uses `$ticket` and `$reviewer` in its body.

```bash
MODEL=haiku tools/run_drill.sh ship-by-arg exercises/ex02-skills/reference 3   # /ship-check LED-105 @dana
```

`Reviewer: @dana` on the note's first line: **3/3** with Haiku. There's no honest red here: when a
skill has no placeholder, Claude Code appends `ARGUMENTS: <what you typed>` anyway. The field buys
named, predictable placement (and the linter checks every name is used), not a different outcome.

---

## 🧰 Tool spotlight: Skillsmith

![A skill that builds and audits other skills](img/skillsmith.png)

[**Skillsmith**](https://github.com/ChristopherKahler/skillsmith) (Christopher Kahler, MIT) is a
*meta-skill*: a skill that builds other skills. We suggest it as an **optional companion** to Steps 1 and 5.

### ❓ Why use it

- 🧩 **Skills have no enforced structure.** Its README names the usual symptoms: entry points that mix
  routing with process logic, tasks that don't read like tasks, no acceptance criteria, skills that
  only work in the author's workspace.
- 📐 **It defines one.** Seven file types, each with a syntax spec (required sections, formats,
  anti-patterns): entry point, task, framework, template, context, checklist, rules.
- 🗣️ **It makes you design before you write.** A guided interview captures the decisions behind
  the skill, which is exactly where a weak `description` (the #1 reason a skill doesn't fire) comes from.
- 🔍 **It audits.** A scored compliance report for one skill or a whole folder: useful for a team's
  growing skill library.

### ⚙️ How it works

| step | command | what you get |
|---|---|---|
| 0 · install | `npx @chrisai/skillsmith --local` | the skill in this project (needs Node 16+). Without `--local` it goes to `~/.claude/commands/`: you only, every project (the Ex 1 trap) |
| 1 · discover | `/skillsmith discover` | an interview (identity → persona → scope → content → review) → `SKILL-SPEC.md` |
| 2 · scaffold | `/skillsmith scaffold` | a skill folder generated from the spec, every file following its type's spec |
| 3 · distill | `/skillsmith distill` | raw material (notes, transcripts) → structured "framework" chunks with when-to-use triggers |
| 4 · audit | `/skillsmith audit` | a compliance score, violations, and what to fix first |

It's pure markdown (no hooks, MCP servers or runtime). Its operational files load on use; its
reference specs are read only when a task needs them, which is the same progressive disclosure you
build by hand in Step 1.

### 🧪 How to use it in this exercise

1. **Before Step 1:** run `/skillsmith discover` for `ship-check`. Bring the spec's *scope* and
   *triggers* into your `description` and `when_to_use`.
2. **After Step 1:** run `/skillsmith audit` on `.claude/skills/ship-check` as a second opinion,
   next to `skill_lint.py`.
3. **Step 5 decides.** Whichever way you wrote it, `skill_eval.py` measures whether it fires, stays
   quiet and beats no skill. A tidy structure is not evidence. A higher recall is.

> ⚠️ **Know before you use it.** It's third-party. Read what it installs, as with any skill. It uses
> its own file types and installs into `.claude/commands/`. **Check where its output lands**: this
> exercise's checks expect `.claude/skills/<name>/SKILL.md`, so you may need to move or adapt the
> scaffold. Not yet tried end-to-end in this workshop: run it once before class.

## 📂 This folder

```
ex02-skills/
├── exercise.html            the student page (7 steps)
├── README.md · LESSONS.md
├── img/                     skills.png · skillsmith.png
├── starter/gates.py         copied into the skill's scripts/ in Step 1
├── evals/ship-check.json    Step 5: should-fire / shouldn't-fire prompts
├── drills/
│   ├── led-120-pr-note/     Steps 0, 2 · prompt · setup.sh (applies LED-105) · the PR-note judge
│   ├── trigger-implicit/    Step 3A · same judge + "did the Skill tool fire?"
│   ├── trigger-quiet/       Step 3B · "did everything stay quiet?"
│   ├── audit-fix/           Step 6a · setup (LED-105 with an ADR-0001 break) · fingerprint judge · variants allowed-only / disallowed
│   ├── release-implicit/    Step 6b · variants no-flag / flag / flag-hook (release skill + scripts/bump.py, + a release-gate hook)
│   ├── release-by-name/     Step 6b · /release must still work
│   ├── paths-payments/      Step 6c · variants none / with-paths / no-paths (currency-rules skill)
│   ├── paths-api/           Step 6c · the skill must stay out of an api/ fix
│   └── ship-by-arg/         Step 6d · /ship-check LED-105 @dana
└── reference/.claude/skills/   🔓 the answer
    ├── ship-check/          SKILL.md · reference.md · scripts/gates.py
    └── adr-audit/           SKILL.md
```

---

## 🧑‍🏫 Before class

1. `tools/doctor.sh`.
2. Record rates with Haiku (implicit firing especially is probabilistic). About 15 min:
   ```bash
   export MODEL=haiku
   tools/run_drill.sh led-120 none 3
   tools/run_drill.sh led-120 exercises/ex02-skills/reference 3
   tools/run_drill.sh trigger-implicit exercises/ex02-skills/reference 3
   tools/run_drill.sh trigger-quiet exercises/ex02-skills/reference 3
   ```
   Step 6 (optional, about 40 min more, run it in the background):
   ```bash
   export MODEL=haiku
   tools/run_drill.sh audit-fix allowed-only 3
   tools/run_drill.sh audit-fix disallowed 3
   tools/run_drill.sh release-implicit no-flag 3
   tools/run_drill.sh release-implicit flag 3
   tools/run_drill.sh release-implicit flag-hook 3
   tools/run_drill.sh release-by-name exercises/ex02-skills/drills/release-implicit/variants/flag-hook 3
   tools/run_drill.sh paths-payments none 3
   tools/run_drill.sh paths-payments with-paths 3
   tools/run_drill.sh paths-api exercises/ex02-skills/drills/paths-payments/variants/with-paths 3
   tools/run_drill.sh ship-by-arg exercises/ex02-skills/reference 3
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
- 🌉 **Step 4, hint 2 is the bridge to Ex 3.** `disallowed-tools` limits the skill's own run; "never
  edit tests/" for every agent is a hook.

## 🖱️ Cursor sidebar

Cursor supports the Agent Skills standard (`SKILL.md` folders); check your version for which
frontmatter fields it honours. `context: fork`, `agent`, `model` and `effort` are Claude Code
fields. The linter's generic checks apply to both.

## 📝 Lessons

See [`LESSONS.md`](LESSONS.md). **Next:** [Ex 3 · Hooks](../ex03-hooks/).
