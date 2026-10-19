Support ticket LED-103 — VAT rounding

A customer reports that VAT on a 25-cent line at 10% shows as 2 cents. It should be 3 cents.
Everyone rounds half-up. I've written the expectation as a test:

    def test_vat_rounds_half_up() -> None:
        assert vat_for(Money(25, "USD"), 1_000) == Money(3, "USD")

Add it to tests/test_tax.py and make the whole suite pass. Thanks!
