# Exercise 4 · Lessons learned

| # | lesson | step |
|---|---|---|
| 1 | Your lockfile is newer than the model's training data. Green tests can sit on a deprecated API | 0 |
| 2 | MCP adds **tools**, not instructions; their schemas cost tokens in every session | 1, 4 |
| 3 | Project scope (`.mcp.json`) is the team's; user scope is just you (the Ex 1 trap again) | 1 |
| 4 | A capability nobody is told to use changes nothing: pair it with a rule | 2 |
| 5 | If you can detect a drift, enforce it: warnings as errors, scoped to the code you own | 3 |
| 6 | Upstream (docs) makes it likely; downstream (a failing test + the finish line) makes it certain | 3 |

## Your numbers

| | before | after |
|---|---|---|
| LED-141 no-deprecated-apis | | |
| LED-141 looked-up-current-docs | | |
| `/context` MCP tools tokens | 0 | |
