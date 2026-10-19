Bug LED-112 — `GET /invoices/999` (an id that doesn't exist) returns 500 Internal Server Error.
It should be a 404. Fix it, following our API conventions, and add a test.
