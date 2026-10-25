## API conventions
- Paths are plural nouns, kebab-case: `/invoices/{id}/refunds`, `/reports/revenue`.
- Amounts in payloads are integers named `*_cents`, with a separate `currency` field.
- Every error response is RFC 9457 problem details: content type `application/problem+json`,
  body `{"type", "title", "status", "detail"}`. The API portal and SDKs parse this shape.
- Map domain exceptions to problems in one place (`api/errors.py`), not in each route.
