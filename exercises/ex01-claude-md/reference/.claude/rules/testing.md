# Testing conventions

- Run with `uv run pytest -q`. Tests marked `landmine` are deselected on purpose; leave them.
- Name tests `test_<behaviour>`, one behaviour per test.
- Use the fixtures in `tests/conftest.py`: `conn` (fresh in-memory DB), `client`, `paid_invoice`.
- Assert money as `Money` or integer `*_cents`, never floats.
- `pytest.raises` always takes `match=` (ruff PT011).
- Never change an existing assertion to make a test pass. If an existing test contradicts the
  request, stop and say so.
