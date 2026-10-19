"""Legacy FX helper ported from the 2019 monolith.

Works on float dollars. Kept only for the old revenue report until it is rewritten.
Superseded by ledgerly.payments.fx (see ADR-0001). Do not use in new code.
"""

RATES = {"USD": 1.0, "EUR": 0.92, "ILS": 3.71, "GBP": 0.79}


def convert(amount: float, src: str, dst: str) -> float:
    """Convert a float amount between currencies, rounded to 2 decimals."""
    return round(amount / RATES[src] * RATES[dst], 2)


def to_display(amount: float, currency: str) -> str:
    return f"{amount:,.2f} {currency}"
