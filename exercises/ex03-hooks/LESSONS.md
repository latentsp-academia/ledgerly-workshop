# Exercise 3 · Lessons learned

> Anything that must happen shouldn't be asked for. Hooks, permissions and scoped settings
> guarantee execution; instructions only make it likely.

| # | lesson | step |
|---|---|---|
| 1 | A hook is code on an event: it runs every time, costs no tokens, and can't be talked out of it | 0 |
| 2 | **Test a hook before wiring it.** A hook you never saw go red is a hope, not evidence | 1 |
| 3 | `deny` for "never", `ask` for "a human decides". Every reason names the legitimate route | 1 |
| 4 | The fence protects itself: hooks and settings are deny, ADRs are ask (no agent ratifies its own rules) | 1 |
| 5 | PostToolUse is edit-time feedback: silent fixes first, talk back only when it can't fix | 2 |
| 6 | A finish line needs three exits: done, not done, and **blocked** (the stop rule) | 3 |
| 7 | Hooks drive "can't" to 0; "tells you about the conflict" stays a rate. Know which is which | 4 |
| 8 | Hooks in the repo are code: the lint gate checks them too | — |

## Your numbers

| check | Ex 1 (advisory) | Ex 3 (hooks) |
|---|---|---|
| LED-103 existing-tests-intact | /5 | /3 |
| LED-103 tax-policy-unchanged | /5 | /3 |
| LED-103 flagged-the-conflict | /5 | /3 |
| LED-132 lint-config-untouched | – | /1 |

**A rule in my own repo that has been broken once and deserves a hook:** …
