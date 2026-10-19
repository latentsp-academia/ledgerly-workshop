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
| 6 | `allowed-tools` pre-approves *and* forbids, which is the difference between "please don't" and "can't" | 4 |
| 7 | `context: fork` + `agent` / `model` / `effort` turn an instruction into a worker; your window gets the answer, not the tool calls | 4 |
| 8 | A skill's sandbox covers its own run, not the session. Rules that must hold for every agent are hooks (Ex 3) | 4 |
| 9 | Evaluate before you trust it: recall, false fires, and quality **against a no-skill baseline**. No gap means no value | 5 |

## Your numbers

| | result |
|---|---|
| `check.sh led-120`: failing checks at Step 0 / Step 2 | / |
| `trigger-implicit` firing rate (`run_drill.sh … current 3`) | /3 |
| `trigger-quiet`: stayed quiet | /3 |
| `/context` Δ tokens: adr-audit **with** fork / **without** | / |
| `skill_eval.py`: recall / false fires / quality with / baseline | / / / |

**A phrase I had to add to `when_to_use` before it fired:** …

**A procedure in my own CLAUDE.md that should be a skill:** …
