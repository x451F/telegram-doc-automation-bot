from decimal import Decimal

from app.services.amount_words import amount_to_words


def test_amount_to_words_zero() -> None:
    assert amount_to_words(Decimal("0")) == "Zero currency units and 00 cents"


def test_amount_to_words_rounding_and_format() -> None:
    assert amount_to_words(Decimal("1234.5")) == (
        "One thousand two hundred thirty-four currency units and 50 cents"
    )


def test_amount_to_words_singular_unit() -> None:
    assert amount_to_words(Decimal("1.01")) == "One currency unit and 01 cents"

