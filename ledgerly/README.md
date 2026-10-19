# Ledgerly

Ledgerly is our invoicing & refunds service.

> ⚠️ Workshop note: this README is **deliberately stale** (docs drift landmine).
> It was last updated in 2021. Compare it to the code and to `docs/decisions/`.
> An agent that trusts it will make wrong choices.

## Getting started

```
pip install -r requirements.txt
make test
python app.py
```

## Stack

- Flask 1.1
- Postgres
- Amounts are stored as decimal dollars (e.g. `12.50`)

## Refunds

Refunds can be partial or full. (They can't. Only full refunds are implemented.)
