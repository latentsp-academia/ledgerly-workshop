# Third-party library APIs

- Training data is older than our lockfile. Before writing code against a library API
  (FastAPI, Pydantic, Starlette, pytest), look it up with the **context7** MCP server:
  `resolve-library-id`, then `query-docs` for the version pinned in `uv.lock`.
- Prefer the current API even when the deprecated one still works. Deprecated today means
  removed in the next upgrade (e.g. FastAPI `lifespan`, not `@app.on_event`; Pydantic
  `field_validator`, not `@validator`).
