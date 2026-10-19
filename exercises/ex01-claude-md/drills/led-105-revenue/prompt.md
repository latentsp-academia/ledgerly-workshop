Ticket LED-105 — Revenue endpoint

Finance wants revenue over HTTP. Add `GET /reports/revenue?currency=EUR`.

Acceptance criteria:
- Sums the captured amount of all **paid** invoices, converted into the requested currency.
- Response body: `{"currency": "EUR", "total_cents": <int>, "invoice_count": <int>}`.
- `currency` defaults to `USD`.

Implement it, make sure it works, and tell me when it's done.
