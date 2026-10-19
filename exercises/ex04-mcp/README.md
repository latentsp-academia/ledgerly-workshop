# Exercise 4 · MCP: current docs upstream, a gate downstream

**4-minute live demo in class · 20 minutes as homework** · Day 1, after the MCP deck (Fundamentals §19)

👉 **Students open [`exercise.html`](exercise.html)** (homework). In class, run Steps 0–2 as a demo
from recorded runs.

## The flow

| step | what happens | checked by | time |
|---|---|---|---|
| 0 · 🔴 Deprecated | LED-141 "seed demo data at startup". Agents often write FastAPI `@app.on_event`, deprecated in the pinned FastAPI. Tests green | `tools/check.sh led-141` → **no-deprecated-apis** + **looked-up-current-docs** red | 5 |
| 1 · 🔌 Connect | `ledgerly/.mcp.json` with Context7 (project scope). `/mcp`, `/context` | `/mcp` shows connected | 4 |
| 2 · 🟢 Use it | `.claude/rules/libraries.md`: look up library APIs with Context7. Same ticket | `check.sh led-141` → GREEN (transcript has `mcp__context7__*`, code uses `lifespan`) | 5 |
| 3 · 🔒 Enforce | A human adds `filterwarnings = ["error::DeprecationWarning:ledgerly"]` (the Ex 3 fence *asks* for pyproject) | pytest fails on the red patch, passes on green | 4 |
| 4 · 💰 Cost | `/context` MCP tools line with and without the server | student's table | 2 |

**In-class demo (4 min):** `tools/demo_reference.sh led-141 red` → show the warning line →
`tools/demo_reference.sh led-141 green` → show the `query-docs` calls in the reference transcript.
Then say: "detect it, and you can enforce it" (Step 3).

## The hidden judge

`drills/led-141-seed/probe_no_deprecated.py` imports the app and runs its startup with every warning
recorded, then keeps only `DeprecationWarning`s raised from `src/ledgerly/`. So a deprecated API in
**our** code fails, and library-internal noise doesn't. Verified against the pinned versions
(FastAPI 0.143: `on_event` warns; Pydantic 2.14: `@validator` warns).

## Context7 facts (checked against context7.com/docs, Oct 2026)

- Remote server: `https://mcp.context7.com/mcp` (HTTP). Local alternative: `npx -y @upstash/context7-mcp`.
- Tools: `resolve-library-id`, `query-docs`. The judge matches any `mcp__context7__*` call.
- API key optional (higher rate limits): `Authorization: Bearer <key>` header. Read it from the
  environment; never commit it.
- Headless: `tools/run_drill.sh` passes `--mcp-config ledgerly/.mcp.json` and allows `mcp__context7`,
  because a headless run can't answer the project-server approval prompt. **Not yet tested with a live
  agent in this workshop: record a run before class.**

## Folder

```
ex04-mcp/
├── exercise.html · README.md · LESSONS.md
├── drills/led-141-seed/    prompt · probes (seed, no-deprecated) · reference red/green + transcripts
└── reference/              .mcp.json · .claude/rules/libraries.md
```

## Cursor sidebar

Cursor reads `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global) with the same
`mcpServers` shape. The judge and the warnings gate are tool-agnostic.
