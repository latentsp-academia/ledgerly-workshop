---
name: release
description: Cuts a Ledgerly release. Bumps the version in pyproject.toml with a script, then writes the release notes for the shipped tickets into CHANGELOG.md.
when_to_use: Use for "release notes", "cut a release", "ship it", "what goes in the changelog", "prepare the release for LED-<n>".
argument-hint: <ticket-id>
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Bash(python3 *), Bash(git log:*), Bash(git diff:*)
---

# Release

1. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/bump.py <ticket>` from the project root. It bumps the
   version and opens a CHANGELOG entry. Note the new version it prints.
2. Replace "(release notes go here)" in CHANGELOG.md with 2–4 user-facing bullets for the ticket,
   based on `git diff HEAD --stat` and the code.
3. Reply with the new version and the notes.
