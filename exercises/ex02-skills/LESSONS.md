# Exercise 2 · Lessons learned

> A skill is a procedure in a folder: a description that decides when it fires, a body that
> arrives pre-filled, and files that cost nothing until they're opened.

| # | lesson | step |
|---|---|---|
| 1 | A team format is a **procedure**, not a fact. In CLAUDE.md it taxes every session; as a skill it costs ~100 tokens until it fires | 0 |
| 2 | Write the **description first**. It's the only part Claude sees before choosing | 1 |
| 3 | `!`cmd`` and scripts put facts in front of the model. A gate table it copies is one it can't make up | 1–2 |
| 4 | Scripts in `.claude/skills/` are code in your repo: your gates lint them too | 1 |
| 5 | Test triggering **both ways**: fires without its name, stays quiet on everything else. Measure a rate | 3 |
| 6 | `allowed-tools` only **pre-approves** (no prompts); every tool stays callable. `disallowed-tools` is what **forbids**: the difference between "please don't" and "can't" | 4 |
| 7 | `context: fork` + `agent` / `model` / `effort` turn an instruction into a worker; your window gets the answer, not the tool calls | 4 |
| 8 | `disallowed-tools` covers the skill's own run, not the session. Rules that must hold for every agent are hooks (Ex 3) | 4 |
| 9 | Evaluate before you trust it: recall, false fires, and quality **against a no-skill baseline**. No gap means no value | 5 |
| 10 | Tools like [Skillsmith](https://github.com/ChristopherKahler/skillsmith) give skills a consistent structure (interview → spec → scaffold → audit). Structure helps people read them; only an eval shows they work | 1, 5 |
| 11 | `disable-model-invocation` stops Claude *calling* a side-effect skill, not reading its script and running it by hand. Only a hook makes "only when a human types /release" hold | 6b |
| 12 | `paths:` loads a skill only for matching files, and `user-invocable: false` keeps background knowledge out of the `/` menu | 6c |
| 13 | `arguments:` gives named, predictable placement (`$ticket`). It doesn't change the outcome: typed arguments are appended anyway | 6d |

## Your numbers

| | result |
|---|---|
| `check.sh led-120`: failing checks at Step 0 / Step 2 | / |
| `trigger-implicit` firing rate (`run_drill.sh … current 3`) | /3 |
| `trigger-quiet`: stayed quiet | /3 |
| `/context` Δ tokens: adr-audit **with** fork / **without** | / |
| `skill_eval.py`: recall / false fires / quality with / baseline | / / / |
| Step 6: audit-fix untouched (allowed-only / disallowed) · release bumped (no-flag / flag-hook) | / · / |

**A phrase I had to add to `when_to_use` before it fired:** …

**A procedure in my own CLAUDE.md that should be a skill:** …
