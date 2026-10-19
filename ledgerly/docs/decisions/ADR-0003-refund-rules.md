---
status: accepted
date: 2023-09-28
---
# ADR-0003: Refund rules

## Decision
- Only `paid` invoices can be refunded.
- The sum of all refunds on an invoice may never exceed `captured_cents`.
- A refund request that would exceed the remaining refundable amount is rejected with HTTP 422
  and the remaining amount in the error body. It is never silently capped.
- Refund rules live in `ledgerly.services.refunds`, not in HTTP handlers.

## Consequences
+ Finance can reconcile refunds against captures one-to-one.
− Partial refunds (not implemented yet, LED-101) must track the running total.
