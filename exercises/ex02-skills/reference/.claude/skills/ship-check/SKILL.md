---
name: ship-check
description: Prepares a Ledgerly change for review. Runs the four quality gates, works out which ADRs the diff touches, and writes the PR note to docs/pr/<ticket>.md in the team's format.
when_to_use: Use when someone wants a change "ready for review", asks for a "PR description" or "PR note", says "make this reviewable", "is this ready to ship", "write up what changed", or is about to open a pull request.
argument-hint: <ticket-id, e.g. LED-105>
allowed-tools: Read, Grep, Glob, Write, Bash(git diff:*), Bash(git status:*), Bash(python3 *), Bash(uv run:*)
---

# Ship check

## Context (filled in before you read this)

Changed files:
!`git status --short`

Diff summary:
!`git diff HEAD --stat`

Gate results (run by the script, not by you):
!`python3 ${CLAUDE_SKILL_DIR}/scripts/gates.py`

## Your task

1. Ticket id: use the argument. If none was given, find `LED-<n>` in the conversation.
2. Read `reference.md` in this skill folder: it has the PR note template and the
   path → ADR map. Follow the template's headings exactly.
3. Copy the gate results table above into **Verification** as-is. Never claim a gate passed
   unless the table says so. If a gate failed, say so and stop: don't fix code from this skill.
4. Write the note to `docs/pr/<ticket>.md` and reply with its path and one line per failed gate.
