"""Text normalization helpers for placeholder and filename generation."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable


WHITESPACE_RE = re.compile(r"\s+")
NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def normalize_whitespace(value: str) -> str:
    """Collapse repeated whitespace and trim leading/trailing spaces."""
    return WHITESPACE_RE.sub(" ", value).strip()


def slugify(value: str) -> str:
    """Convert text into a lowercase ASCII slug."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    stripped = NON_ALNUM_RE.sub("-", normalized.lower()).strip("-")
    return stripped or "item"


def safe_filename(value: str, max_length: int = 80) -> str:
    """Build a filesystem-safe filename stem with deterministic fallback."""
    normalized = slugify(normalize_whitespace(value))
    if len(normalized) <= max_length:
        return normalized
    return normalized[:max_length].rstrip("-")


def join_non_empty(items: Iterable[str], separator: str = ", ") -> str:
    """Join only non-empty normalized values into one display string."""
    prepared = [normalize_whitespace(item) for item in items if normalize_whitespace(item)]
    return separator.join(prepared)

