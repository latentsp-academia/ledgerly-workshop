# Exercise 1 · Lessons learned

> CLAUDE.md is the cheapest fix for *missing knowledge*. It's also advisory: it moves a rate, it
> doesn't guarantee one.

| # | lesson | step |
|---|---|---|
| 1 | Run the check **before** the agent: red first, so you know the check can fail | 1 |
| 2 | **Green tests ≠ correct.** The agent's own tests passed and it said "done". A hidden check said no | 3 |
| 3 | No agent can guess a team rule that isn't in the code. That's what CLAUDE.md is for | 4 |
| 4 | Test each line: *would the agent get this wrong without it?* If not, delete it | 4 |
| 5 | Say how to verify: the real commands and what "done" means | 4 |
| 6 | Same ticket, one file added, red → green. Change one thing at a time | 5 |
| 7 | One run proves nothing. Measure a rate: `run_drill.sh … 3` | 6 |
| 8 | A team rule lives in the project file, in git. Never only in `~/.claude/CLAUDE.md` | 4 |
| 9 | Part 2: CLAUDE.md fixes *facts* (commands, done means); house style the code doesn't show needs a `.claude/rules/` topic file | 8–9 |
| 10 | CLAUDE.md is a suggestion. When a miss is expensive, enforce it with a hook (Ex 3) | 10 |

## Your numbers

| | no CLAUDE.md | your CLAUDE.md |
|---|---|---|
| `tools/check.sh led-107`: verdict | | |
| what the agent returned for 100.00 / 3 | | |
| `run_drill.sh led-107 … 3`: `split-is-exact` | /3 | /3 |
| lines in your CLAUDE.md | 0 | |
| `tools/check.sh led-105`: failing checks (none / CLAUDE.md / + rule) | | |
| LED-103: runs where the agent edited a test or `tax.py` | /3 | /3 |

**The line in my CLAUDE.md that did the most work:** …

**A rule from my own codebase that no agent could guess:** …
