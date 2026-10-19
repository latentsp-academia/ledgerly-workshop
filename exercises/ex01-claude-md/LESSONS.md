# Exercise 1 · Lessons learned

> CLAUDE.md is the cheapest, highest-leverage fix for *missing knowledge*, and it's still
> advisory. It moves the agent from "wrong" to "usually right". It can't make anything certain.

| # | lesson | step |
|---|---|---|
| 1 | Without memory, the agent's truth is whatever it reads first: stale README, nearby legacy code, training data | 0 |
| 2 | **Green tests ≠ no drift.** Decide what drift means for your repo, then make it checkable | 0 |
| 3 | Write only what the code can't say: commands, the finish line, what's legacy, where decisions live | 1 |
| 4 | Directory-level files load **lazily**: cheap for everyone, invisible until Claude works in that folder | 2 |
| 5 | House style the code doesn't show (`kw_only`, no dicts from services) only reaches the agent through a rule. Grade it with a check the agent can't see | 3 |
| 5b | `.claude/rules/` splits CLAUDE.md by topic; without `paths:` a rule costs the same as CLAUDE.md | 3 |
| 6 | `@` imports organise. They load **eagerly**, so splitting doesn't save context | 4 |
| 7 | `/context` and `/memory` only *report*. First question for an ignored rule: did it even load? | 5 |
| 8 | User-level config isn't in git. A team convention there is "works on my machine" | 6 |
| 9 | Memory files are concatenated, not overridden. Only settings have precedence | — |
| 10 | Advisory gives you a rate. If one failure is costly, it needs enforcement (Ex 3) | close |

## Your numbers

| | Step 0 (none) | Step 1 (yours) | reference |
|---|---|---|---|
| `tools/check.sh led-105`: failing checks | | | |
| value-object-convention after Step 1 / Step 3 | | | |
| `/context` memory tokens | 0 | | ~410 |
| LED-112: team-error-convention, Dev A / Dev B | | | |

**The line in my CLAUDE.md that did the most work:** …

**Something in my own `~/.claude/CLAUDE.md` that actually belongs in a project:** …
