"""Validation and parsing helpers for conversational document intake."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.services.date_utils import parse_date
from app.services.text_utils import normalize_whitespace


def parse_non_empty_text(value: str, field_name: str) -> str:
    """Normalize and validate non-empty text field values."""
    normalized = normalize_whitespace(value)
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty.")
    return normalized


def parse_positive_int(value: str, field_name: str, minimum: int = 1, maximum: int = 20) -> int:
    """Parse and validate positive integer values in an expected range."""
    try:
        parsed = int(value.strip())
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a whole number.") from exc

    if parsed < minimum or parsed > maximum:
        raise ValueError(f"{field_name} must be between {minimum} and {maximum}.")
    return parsed


def parse_decimal_amount(value: str, field_name: str) -> Decimal:
    """Parse and validate positive monetary values."""
    normalized = value.strip().replace(" ", "").replace(",", ".")
    try:
        parsed = Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} must be a valid decimal number.") from exc

    if parsed <= Decimal("0"):
        raise ValueError(f"{field_name} must be greater than zero.")
    return parsed.quantize(Decimal("0.01"))


def parse_date_input(value: str, field_name: str) -> str:
    """Parse user-provided date and return canonical ISO representation."""
    try:
        parsed = parse_date(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD, DD.MM.YYYY, or DD/MM/YYYY.") from exc
    return parsed.isoformat()

