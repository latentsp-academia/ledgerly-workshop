LED-151 — Write tests for refunds from the contract, not from the code.

Read docs/decisions/ADR-0003-refund-rules.md. For each rule in it, write a test named after the rule
that checks the observable behaviour (HTTP status codes, response bodies, amounts left to refund)
through the API or the service, never private details. Include the boundaries: refunding exactly
what's left, one cent more than what's left, several partial refunds in a row, and an invoice that
was never paid. Write each test so that it would fail if the rule were broken, then run them.
Don't change the refund code.
