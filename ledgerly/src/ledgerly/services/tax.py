"""VAT calculation. Rounding policy is fixed by ADR-0004 (half-even)."""

from __future__ import annotations

from decimal import ROUND_HALF_EVEN, Decimal

from ledgerly.payments.money import Money

DEFAULT_VAT_RATE_BP = 1_700  # 17.00%


def vat_for(net: Money, rate_bp: int = DEFAULT_VAT_RATE_BP) -> Money:
    """VAT on ``net`` at ``rate_bp`` basis points, rounded half-even to whole cents."""
    if rate_bp < 0:
        raise ValueError("VAT rate cannot be negative")
    amount = (Decimal(net.cents) * rate_bp / Decimal(10_000)).quantize(
        Decimal(1), rounding=ROUND_HALF_EVEN
    )
    return Money(int(amount), net.currency)
