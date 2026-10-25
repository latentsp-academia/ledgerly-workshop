---
name: currency-rules
description: Ledgerly's rules for adding or changing a currency in the payments package (Money, fx rates, supported currencies).
when_to_use: Use when adding a currency, changing an FX rate, or touching SUPPORTED_CURRENCIES or DEFAULT_RATES_BP.
user-invocable: false
paths: src/ledgerly/payments/**
---

# Currency rules (finance signs off on these)

Adding a currency takes three changes, all in one PR:

1. `SUPPORTED_CURRENCIES` in `payments/money.py`.
2. A rate in `DEFAULT_RATES_BP` in `payments/fx.py` (basis points per 1 USD).
3. A round-trip test in `tests/test_money.py` named exactly `test_<code>_round_trip`
   (lowercase code, e.g. `test_chf_round_trip`): convert 100.00 USD to the new currency and
   back, and assert the result is within 1 cent of 10_000. Finance's reconciliation job greps
   for these names.
