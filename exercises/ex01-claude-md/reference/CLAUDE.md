# Ledgerly

Invoicing & refunds HTTP API. Python 3.11+, FastAPI, SQLite, managed with **uv**.
README.md is stale (Flask/Postgres/make era): trust this file and `pyproject.toml`.

@docs/standards/api-conventions.md

## Commands
- Install: `uv sync`
- Tests: `uv run pytest -q`
- Lint: `uv run ruff check . && uv run ruff format --check .`
- Architecture contracts: `uv run lint-imports`

## Done means
All four are green: pytest, ruff check, ruff format --check, lint-imports.
New behaviour has a test. Report which commands you ran and their result.

## Layout
- `src/ledgerly/api/`: HTTP only. Imports services, never repo (ADR-0002).
- `src/ledgerly/services/`: all business rules.
- `src/ledgerly/repo/db.py`: SQL. Only services import it.
- `src/ledgerly/payments/`: `Money` (integer cents) and FX. Has its own CLAUDE.md.
- `docs/decisions/`: ADRs. Read the relevant one before changing that area.

## Money (ADR-0001)
- Amounts are `Money(cents: int, currency)`; convert with `payments.fx.convert`.
- `payments/legacy_fx.py` and `services/reports.py` are float legacy. Don't build on them.

## When a request conflicts with an ADR
Stop and say so. Don't work around it.
