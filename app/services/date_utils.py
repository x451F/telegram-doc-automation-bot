"""Utility helpers for parsing and formatting dates in bot workflows."""

from __future__ import annotations

from datetime import date, datetime
from typing import Sequence


DEFAULT_INPUT_FORMATS: tuple[str, ...] = (
    "%Y-%m-%d",
    "%d.%m.%Y",
    "%d/%m/%Y",
)


def parse_date(value: str, formats: Sequence[str] = DEFAULT_INPUT_FORMATS) -> date:
    """Parse a date string into `datetime.date` using known input formats."""
    normalized_value = value.strip()
    for fmt in formats:
        try:
            return datetime.strptime(normalized_value, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {value!r}")


def format_date(value: date, output_format: str = "%Y-%m-%d") -> str:
    """Format `datetime.date` to a string for document placeholders."""
    return value.strftime(output_format)


def today_iso() -> str:
    """Return current date as ISO string for default form values."""
    return date.today().isoformat()

