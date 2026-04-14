from decimal import Decimal

from app.services.validation import parse_decimal_amount


def test_amount_normalization_accepts_spaces_and_comma() -> None:
    assert parse_decimal_amount(" 1 234,5 ", "amount") == Decimal("1234.50")

