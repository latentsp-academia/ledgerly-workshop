---
name: adr-audit
description: Audits the current diff against Ledgerly's architecture decision records and reports violations worst-first. Read-only; never edits files.
when_to_use: Use for "check this against the ADRs", "does this break any decisions", "architecture review", "audit the diff", or before a reviewer looks at a change.
allowed-tools: Read, Grep, Glob, Bash(git diff:*)
context: fork
agent: Explore
model: haiku
effort: low
---

# ADR audit

Diff under review:
!`git diff HEAD --stat`

1. Read every file in `docs/decisions/`.
2. For each changed file above, check it against each ADR that applies.
3. Report findings worst-first: `ADR-000N · file:line · what breaks it · suggested fix`.
4. If nothing breaks, say "No ADR violations" and list which ADRs you checked.

You cannot edit files from this skill. If asked to fix something, report the fix instead.
