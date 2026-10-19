# Exercise 0 · Lessons learned

> Know the ground before you judge the agent: green gates, the app's real rules, and where the
> judge lives.

| # | lesson | step |
|---|---|---|
| 1 | Get every gate green **before** the agent starts, or every result after is noise | 0 |
| 2 | Ledgerly's rules live in the ADRs and the code, enforced by import-linter, not in the README | 1 |
| 3 | Real repos lie: a stale README, legacy code, protected files. An agent reads them all | 2 |
| 4 | Every exercise has the same shape: page · drills (prompt, checks, probes, reference patches) · reference · README · LESSONS | 3 |
| 5 | Judges and answers live in `exercises/`, outside the app, so the agent can't read them | 3 |
| 6 | Read the check report, not the agent's summary | 4 |
| 7 | One run proves little. Every exercise measures rates | 4 |

## Your numbers

| | result |
|---|---|
| `tools/doctor.sh` | READY · warnings: |
| LED-100 `tools/check.sh` | red · green · failing check: |
| did the agent add a test without being asked? | yes · no |

**One landmine I've seen in a real repo of mine:** …
