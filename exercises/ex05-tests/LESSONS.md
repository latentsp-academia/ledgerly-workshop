# Exercise 5 · Lessons learned

> A test is evidence only if it would fail on a broken version. Everything downstream (the finish
> line, CI) is only as strong as the tests it runs.

| # | lesson | step |
|---|---|---|
| 1 | "Write tests for X" gets a description of X. Tests written from the code pass by construction | 0 |
| 2 | Score tests by **mutants killed**. Coverage and test count both reward mirror tests | 0 |
| 3 | Read before you keep: rule-checks stay, mirrors and duplicates go | 1 |
| 4 | A good test ask has a **source** (ADR/spec), **names** (a rule each), **boundaries** and a **fence** (don't touch the code) | 2 |
| 5 | The judge finds the gap and the agent closes it: paste the surviving mutant back as the next prompt | 2 |
| 6 | "Make it pass" is a trap. Skip, retry and shrink are all green and all keep the bug | 3 |
| 7 | A fence guards **edits**, a judge guards **outcomes**. An added `skip` line passes an append-only fence | 3 |
| 8 | Flaky is a bug report. Here, two customers could get the same invoice number | 3 |

## Your numbers

| check | weak ask (LED-150) | contract ask (LED-151) |
|---|---|---|
| mutants killed | /7 | /7 |
| tests written | | |
| ✅ rule · 🪞 mirror · ♻️ duplicate | · · | · · |

| LED-118 | result |
|---|---|
| what the agent changed first | test · code |
| check.sh led-118 | red · green |

**A test in my own repo that would survive a mutant:** …
