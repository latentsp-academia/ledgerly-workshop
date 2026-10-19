import pytest

from ledgerly.payments.money import Money
from ledgerly.services.tax import vat_for


@pytest.mark.parametrize(
    ("net_cents", "rate_bp", "expected"),
    [
        (10_000, 1_700, 1_700),
        (0, 1_700, 0),
        (250, 1_000, 25),
        (25, 1_000, 2),  # 2.5 -> 2 (half-even, ADR-0004)
        (35, 1_000, 4),  # 3.5 -> 4 (half-even, ADR-0004)
    ],
)
def test_vat_half_even(net_cents: int, rate_bp: int, expected: int) -> None:
    assert vat_for(Money(net_cents, "USD"), rate_bp) == Money(expected, "USD")


def test_negative_rate_rejected() -> None:
    with pytest.raises(ValueError, match="negative"):
        vat_for(Money(100, "USD"), -1)
