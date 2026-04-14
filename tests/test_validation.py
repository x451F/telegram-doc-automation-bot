from decimal import Decimal

import pytest

from app.services.validation import (
    parse_date_input,
    parse_decimal_amount,
    parse_non_empty_text,
    parse_positive_int,
)


def test_parse_non_empty_text() -> None:
    assert parse_non_empty_text("  sample  ", "field") == "sample"
    with pytest.raises(ValueError):
        parse_non_empty_text("   ", "field")


def test_parse_positive_int() -> None:
    assert parse_positive_int("3", "work item count") == 3
    with pytest.raises(ValueError):
        parse_positive_int("0", "work item count")


def test_parse_decimal_amount() -> None:
    assert parse_decimal_amount("1000,5", "amount") == Decimal("1000.50")
    with pytest.raises(ValueError):
        parse_decimal_amount("-1", "amount")


def test_parse_date_input() -> None:
    assert parse_date_input("2026-04-14", "date") == "2026-04-14"
    with pytest.raises(ValueError):
        parse_date_input("2026/14/14", "date")

