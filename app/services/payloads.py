"""Typed payload models for collected document intake data."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping


@dataclass(slots=True, frozen=True)
class DocumentIntakePayload:
    """Final collected fields from the intake FSM flow."""

    document_type: str
    contract_number: str
    contract_date: str
    work_items: tuple[str, ...]
    contract_total_amount: Decimal
    net_amount: Decimal
    certificate_number: str
    certificate_date: str
    amount_in_words: str


def build_payload(data: Mapping[str, Any]) -> DocumentIntakePayload:
    """Construct a strongly typed payload object from FSM storage."""
    return DocumentIntakePayload(
        document_type=str(data["document_type"]),
        contract_number=str(data["contract_number"]),
        contract_date=str(data["contract_date"]),
        work_items=tuple(str(item) for item in data.get("work_items", [])),
        contract_total_amount=Decimal(str(data["contract_total_amount"])),
        net_amount=Decimal(str(data["net_amount"])),
        certificate_number=str(data["certificate_number"]),
        certificate_date=str(data["certificate_date"]),
        amount_in_words=str(data["amount_in_words"]),
    )


def format_payload_summary(payload: DocumentIntakePayload) -> str:
    """Render a human-readable summary to confirm collected values."""
    work_items_lines = "\n".join(
        f"{index}. {item}" for index, item in enumerate(payload.work_items, start=1)
    )
    document_type = payload.document_type.replace("_", " ").title()

    return (
        "Collected payload preview:\n"
        f"- Document type: {document_type}\n"
        f"- Contract number: {payload.contract_number}\n"
        f"- Contract date: {payload.contract_date}\n"
        f"- Work items ({len(payload.work_items)}):\n{work_items_lines}\n"
        f"- Contract total amount: {payload.contract_total_amount}\n"
        f"- Net amount: {payload.net_amount}\n"
        f"- Certificate number: {payload.certificate_number}\n"
        f"- Certificate date: {payload.certificate_date}\n"
        f"- Amount in words: {payload.amount_in_words}"
    )

