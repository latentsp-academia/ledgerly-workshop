-- 001_init.sql — applied to production 2023-02-11.
-- Applied migrations are immutable. To change the schema, add a new numbered file.
CREATE TABLE IF NOT EXISTS invoices (
    id             INTEGER PRIMARY KEY,
    number         TEXT    NOT NULL UNIQUE,
    customer       TEXT    NOT NULL,
    currency       TEXT    NOT NULL,
    net_cents      INTEGER NOT NULL,
    vat_cents      INTEGER NOT NULL,
    status         TEXT    NOT NULL DEFAULT 'open',
    captured_cents INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS invoice_lines (
    id          INTEGER PRIMARY KEY,
    invoice_id  INTEGER NOT NULL REFERENCES invoices(id),
    description TEXT    NOT NULL,
    quantity    INTEGER NOT NULL,
    unit_cents  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log_old (
    id      INTEGER PRIMARY KEY,
    message TEXT
);
