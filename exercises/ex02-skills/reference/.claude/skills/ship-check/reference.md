# PR note template (Ledgerly)

Use these headings, in this order, exactly as written.

```markdown
# <ticket>: <one-line title>

## Ticket
<ticket id> · <one sentence: what was asked>

## Summary
- <what changed, one bullet per behaviour, in plain words>

## ADRs touched
- ADR-000N <title>: <how this change respects it, one line>

## Verification
<the gate results table from the skill context, unchanged>

## Risk & rollback
- Risk: <what could break, who would notice>
- Rollback: <revert the commit / feature is additive / migration needed?>

## Changelog
- <YYYY-MM-DD> <METHOD /path or area> — <what changed>
```

## Path → ADR map

| the diff touches… | list |
|---|---|
| anything with money, `payments/`, currency conversion, amounts in payloads | ADR-0001 money as integer cents |
| a new route, `api/`, or a new `services/` module | ADR-0002 layered architecture |
| `services/refunds.py`, `api/routes_refunds.py`, refund rules | ADR-0003 refund rules |
| `services/tax.py`, VAT | ADR-0004 VAT rounding |

List every ADR that applies. If none do, write "None" and say why.
