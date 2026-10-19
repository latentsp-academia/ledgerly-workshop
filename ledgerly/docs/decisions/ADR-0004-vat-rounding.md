---
status: accepted
date: 2024-01-15
---
# ADR-0004: VAT rounds half-even (banker's rounding)

## Context
Our tax authority audit requires that aggregated VAT across many invoices does not drift upward.
Half-up rounding on every line biased totals by +0.5 cent on average.

## Considered
- Half-up. What customers intuitively expect; audit found systematic upward bias.
- **Half-even. Chosen.** Unbiased over many invoices.

## Decision
VAT is computed in `ledgerly.services.tax.vat_for` with `ROUND_HALF_EVEN`. 2.5 cents → 2, 3.5 → 4.

## Consequences
− Customers occasionally report "wrong" rounding. That is expected; route them to finance.
− Changing this needs finance sign-off and a new ADR that supersedes this one.
