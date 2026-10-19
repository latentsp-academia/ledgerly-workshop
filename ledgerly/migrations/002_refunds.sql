-- 002_refunds.sql — applied to production 2023-09-30.
CREATE TABLE IF NOT EXISTS refunds (
    id           INTEGER PRIMARY KEY,
    invoice_id   INTEGER NOT NULL REFERENCES invoices(id),
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    created_at   TEXT    NOT NULL
);
