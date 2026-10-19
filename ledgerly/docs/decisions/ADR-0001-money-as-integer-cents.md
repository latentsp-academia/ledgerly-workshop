---
status: accepted
date: 2023-02-02
---
# ADR-0001: Money is integer cents, never floats

## Context
The 2019 monolith stored dollars as floats. Refund reconciliation drifted by up to 3 cents per
thousand invoices, and finance spent two weeks a quarter hand-correcting ledgers.

## Considered
- Floats, rounded at display time. Simple, and the exact cause of the drift.
- `Decimal` everywhere. Correct, but leaks into JSON and DB types inconsistently.
- **Integer minor units (cents) in a `Money` value object. Chosen.**

## Decision
- All amounts are `ledgerly.payments.money.Money(cents: int, currency: str)`.
- API payloads expose amounts as integer fields named `*_cents`.
- Currency conversion goes through `ledgerly.payments.fx.convert`, which uses basis-point rates
  and rounds half-even exactly once.
- `ledgerly.payments.legacy_fx` (floats) is frozen. Only the legacy revenue report may import it.

## Consequences
+ No cumulative rounding drift.
− Every display layer must format cents itself.
− Do NOT "simplify" by passing floats around because a report needs dollars.
