LED-141 — Demo environments start empty, which makes sales demos awkward. When the environment
variable LEDGERLY_SEED=1 is set, seed two demo invoices when the application starts: one for
"Demo Co" (USD, 1 line of 10000 cents) that is captured, and one for "Sample GmbH" (EUR, 1 line of
5000 cents) left open. Without the variable, nothing is seeded. Add a test.
