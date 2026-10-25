# Ledgerly
Invoicing API. Python 3.11, FastAPI, SQLite, uv. README.md is stale: trust this file.

## Commands
- Tests: `uv run pytest -q` · Lint: `uv run ruff check .` · Architecture: `uv run lint-imports`

## Done means
All three green, and new behaviour has a test.

## Money (ADR-0001)
- Amounts are integer cents (`Money`). Never floats.
- Splitting an amount: every part is `total // n` cents and the LAST part absorbs the
  remainder. 100.00 / 3 → 33.33, 33.33, 33.34.
