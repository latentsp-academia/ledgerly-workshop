"""Money value object. All amounts are integer minor units (cents). See ADR-0001."""

from __future__ import annotations

from dataclasses import dataclass

SUPPORTED_CURRENCIES = frozenset({"USD", "EUR", "ILS", "GBP"})


class CurrencyMismatchError(ValueError):
    """Raised when combining Money values in different currencies."""


@dataclass(frozen=True, slots=True)
class Money:
    cents: int
    currency: str

    def __post_init__(self) -> None:
        if isinstance(self.cents, bool) or not isinstance(self.cents, int):
            raise TypeError(
                f"Money.cents must be an int, got {type(self.cents).__name__} (ADR-0001)"
            )
        if self.currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {self.currency!r}")

    @classmethod
    def zero(cls, currency: str) -> Money:
        return cls(0, currency)

    def _same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(f"{self.currency} != {other.currency}")

    def __add__(self, other: Money) -> Money:
        self._same_currency(other)
        return Money(self.cents + other.cents, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._same_currency(other)
        return Money(self.cents - other.cents, self.currency)

    def __mul__(self, factor: int) -> Money:
        if isinstance(factor, bool) or not isinstance(factor, int):
            raise TypeError("Money can only be multiplied by an int (quantities)")
        return Money(self.cents * factor, self.currency)

    def __lt__(self, other: Money) -> bool:
        self._same_currency(other)
        return self.cents < other.cents

    def __le__(self, other: Money) -> bool:
        self._same_currency(other)
        return self.cents <= other.cents
