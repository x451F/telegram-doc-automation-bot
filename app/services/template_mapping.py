"""Mapping layer from FSM payload to DOCX template placeholders."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.payloads import DocumentIntakePayload
from app.services.text_utils import normalize_whitespace


MAX_WORK_PLACEHOLDERS = 5
DEFAULT_CITY = "Sample City"


@dataclass(slots=True, frozen=True)
class TemplatePlaceholderMapping:
    """Placeholder dictionaries per template type."""

    contract: dict[str, str]
    completion_certificate: dict[str, str]


def _format_amount(value: object) -> str:
    return f"{value:.2f}"


def _normalize_city(city: str | None) -> str:
    if city is None:
        return DEFAULT_CITY
    normalized = normalize_whitespace(city)
    return normalized if normalized else DEFAULT_CITY


def _build_work_slots(work_items: tuple[str, ...], slots: int = MAX_WORK_PLACEHOLDERS) -> list[str]:
    normalized_items = [normalize_whitespace(item) for item in work_items if normalize_whitespace(item)]
    if len(normalized_items) <= slots:
        return normalized_items + [""] * (slots - len(normalized_items))

    preserved = normalized_items[: slots - 1]
    collapsed_tail = "; ".join(normalized_items[slots - 1 :])
    return preserved + [collapsed_tail]


def _build_work_placeholders(prefix: str, work_slots: list[str]) -> dict[str, str]:
    output: dict[str, str] = {}
    for index, value in enumerate(work_slots, start=1):
        output[f"[{prefix}_work_{index}]"] = value
    return output


def build_template_mapping(
    payload: DocumentIntakePayload,
    city: str | None = None,
) -> TemplatePlaceholderMapping:
    """Build placeholder mappings for contract and completion templates."""
    normalized_city = _normalize_city(city)
    work_slots = _build_work_slots(payload.work_items, slots=MAX_WORK_PLACEHOLDERS)

    common_placeholders = {
        "[contract_number]": payload.contract_number,
        "[contract_date]": payload.contract_date,
        "[city]": normalized_city,
        "[contract_total_amount]": _format_amount(payload.contract_total_amount),
        "[net_amount]": _format_amount(payload.net_amount),
        "[certificate_number]": payload.certificate_number,
        "[certificate_date]": payload.certificate_date,
        "[certificate_amount]": _format_amount(payload.contract_total_amount),
        "[certificate_amount_text]": payload.amount_in_words,
    }

    contract_mapping = {
        **common_placeholders,
        **_build_work_placeholders("contract", work_slots),
        **_build_work_placeholders("certificate", work_slots),
    }
    completion_mapping = {
        **common_placeholders,
        **_build_work_placeholders("contract", work_slots),
        **_build_work_placeholders("certificate", work_slots),
    }

    return TemplatePlaceholderMapping(
        contract=contract_mapping,
        completion_certificate=completion_mapping,
    )

