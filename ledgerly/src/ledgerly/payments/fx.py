"""Currency conversion on integer cents. This is the module to use (ADR-0001).

Rates are expressed in basis points of 1 USD (10_000 == 1.0000) so no floats are involved.
Rounding is half-even, applied exactly once at the end of a conversion.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import ROUND_HALF_EVEN, Decimal

from ledgerly.payments.money import Money

# Units of currency per 1 USD, in basis points. Refreshed nightly in production.
DEFAULT_RATES_BP: Mapping[str, int] = {
    "USD": 10_000,
    "EUR": 9_200,
    "ILS": 37_100,
    "GBP": 7_900,
}


class UnsupportedConversionError(KeyError):
    """No rate is known for the requested currency."""


def convert(money: Money, to: str, rates_bp: Mapping[str, int] = DEFAULT_RATES_BP) -> Money:
    """Convert ``money`` into currency ``to``. Returns a new Money in integer cents."""
    if money.currency == to:
        return money
    try:
        src, dst = rates_bp[money.currency], rates_bp[to]
    except KeyError as exc:
        raise UnsupportedConversionError(str(exc)) from exc
    cents = (Decimal(money.cents) * dst / src).quantize(Decimal(1), rounding=ROUND_HALF_EVEN)
    return Money(int(cents), to)
