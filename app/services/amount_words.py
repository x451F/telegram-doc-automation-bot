"""Amount-to-words conversion helpers for English document placeholders."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

_ONES = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
)
_TENS = (
    "",
    "",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
)
_SCALES = (
    (1_000_000_000, "billion"),
    (1_000_000, "million"),
    (1_000, "thousand"),
)


def _convert_hundreds(value: int) -> str:
    if value < 20:
        return _ONES[value]
    if value < 100:
        tens = value // 10
        remainder = value % 10
        if remainder == 0:
            return _TENS[tens]
        return f"{_TENS[tens]}-{_ONES[remainder]}"

    hundreds = value // 100
    remainder = value % 100
    if remainder == 0:
        return f"{_ONES[hundreds]} hundred"
    return f"{_ONES[hundreds]} hundred {_convert_hundreds(remainder)}"


def _integer_to_words(value: int) -> str:
    if value < 0:
        raise ValueError("Amount cannot be negative.")
    if value == 0:
        return "zero"
    if value < 1000:
        return _convert_hundreds(value)

    chunks: list[str] = []
    remaining = value
    for scale_value, scale_name in _SCALES:
        if remaining >= scale_value:
            chunk = remaining // scale_value
            remaining = remaining % scale_value
            chunks.append(f"{_convert_hundreds(chunk)} {scale_name}")
    if remaining > 0:
        chunks.append(_convert_hundreds(remaining))
    return " ".join(chunks)


def amount_to_words(amount: Decimal) -> str:
    """Convert decimal amount to English words for generic currency text."""
    if amount < Decimal("0"):
        raise ValueError("Amount cannot be negative.")

    normalized = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    major = int(normalized)
    minor = int((normalized - Decimal(major)) * 100)

    major_words = _integer_to_words(major)
    major_label = "currency unit" if major == 1 else "currency units"
    sentence = f"{major_words} {major_label} and {minor:02d} cents"
    return sentence[0].upper() + sentence[1:]
