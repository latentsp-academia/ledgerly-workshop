Ticket LED-107 — Pay in installments

Customers want to pay an invoice in installments. Add
`GET /invoices/{id}/installments?count=3` that splits the invoice total into `count` payments.

Response body: `{"invoice_id": 1, "count": 3, "installments": [...]}`, one amount per payment.
Example: a 100.00 invoice paid in 3 installments.

Implement it, make sure it works, and tell me when it's done.
