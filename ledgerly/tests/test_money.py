import pytest

from ledgerly.payments.fx import convert
from ledgerly.payments.money import CurrencyMismatchError, Money


def test_money_rejects_floats() -> None:
    with pytest.raises(TypeError):
        Money(12.5, "USD")  # type: ignore[arg-type]


def test_money_adds_same_currency() -> None:
    assert Money(150, "USD") + Money(50, "USD") == Money(200, "USD")


def test_money_refuses_mixed_currency() -> None:
    with pytest.raises(CurrencyMismatchError):
        Money(1, "USD") + Money(1, "EUR")


def test_fx_convert_usd_to_eur_in_cents() -> None:
    assert convert(Money(10_000, "USD"), "EUR") == Money(9_200, "EUR")


def test_fx_convert_rounds_half_even() -> None:
    # 1 cent USD -> 0.92 EUR cents -> rounds to 1
    assert convert(Money(1, "USD"), "EUR") == Money(1, "EUR")


def test_fx_same_currency_is_identity() -> None:
    m = Money(123, "ILS")
    assert convert(m, "ILS") is m
