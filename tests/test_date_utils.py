from datetime import date

from app.services.date_utils import format_date, parse_date


def test_parse_date_supports_multiple_formats() -> None:
    assert parse_date("2026-04-14") == date(2026, 4, 14)
    assert parse_date("14.04.2026") == date(2026, 4, 14)
    assert parse_date("14/04/2026") == date(2026, 4, 14)


def test_format_date_iso_default() -> None:
    assert format_date(date(2026, 4, 14)) == "2026-04-14"

