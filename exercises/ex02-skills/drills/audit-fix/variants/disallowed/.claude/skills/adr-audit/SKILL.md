---
name: adr-audit
description: Audits the current diff against Ledgerly's architecture decision records and reports violations worst-first.
when_to_use: Use for "check this against the ADRs", "does this break any decisions", "architecture review", "audit the diff".
allowed-tools: Read, Grep, Glob, Bash(git diff:*)
disallowed-tools: Write, Edit, NotebookEdit, Bash(python*), Bash(sed*)
---

# ADR audit

Diff under review:
!`git diff HEAD --stat`

1. Read every file in `docs/decisions/`.
2. Check each changed file above against each ADR that applies.
3. Report findings worst-first: `ADR-000N · file:line · what breaks it · suggested fix`.
