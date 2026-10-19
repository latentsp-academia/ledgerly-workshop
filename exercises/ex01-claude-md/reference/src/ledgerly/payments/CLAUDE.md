# payments/: money primitives (ADR-0001)

- `Money(cents: int, currency)` rejects floats on purpose. Don't "fix" that.
- Convert with `fx.convert(money, to)`: basis-point rates, half-even rounding applied once.
- `legacy_fx.py` is frozen float code for the old revenue report only.
  New code never imports it (import-linter enforces this for api/ and services/).
- Supported currencies live in `money.SUPPORTED_CURRENCIES`. Adding one needs a rate in `fx.py`.
