---
status: accepted
date: 2023-03-20
---
# ADR-0002: Layered architecture — api → services → repo

## Context
Business rules were duplicated between HTTP handlers and batch jobs, and they diverged.

## Considered
- Fat handlers. Fast to write, rules end up in three places.
- **Three layers: `api` (HTTP only) → `services` (rules) → `repo` (SQL). Chosen.**

## Decision
- `ledgerly.api` may import `ledgerly.services` and `ledgerly.payments`, never `ledgerly.repo`.
- `ledgerly.services` owns all business rules.
- Enforced by import-linter (`.importlinter`, run `uv run lint-imports`).
- Known exception: `api/routes_refunds.py` predates this ADR and is listed in `ignore_imports`.
  The exception is a debt to pay down, not a pattern to copy.

## Consequences
+ One place per rule.
− Small features touch three files.
