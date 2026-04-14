from decimal import Decimal

from app.services.payloads import DocumentIntakePayload
from app.services.template_mapping import build_template_mapping


def _payload_with_items(*items: str) -> DocumentIntakePayload:
    return DocumentIntakePayload(
        document_type="service_agreement",
        contract_number="AGR-2026-011",
        contract_date="2026-04-14",
        work_items=tuple(items),
        contract_total_amount=Decimal("1000.00"),
        net_amount=Decimal("900.00"),
        certificate_number="CERT-2026-011",
        certificate_date="2026-04-15",
        amount_in_words="Nine hundred currency units",
    )


def test_build_template_mapping_populates_expected_placeholders() -> None:
    payload = _payload_with_items("Analysis", "Implementation")
    mapping = build_template_mapping(payload, city="Paris")

    assert mapping.contract["[contract_number]"] == "AGR-2026-011"
    assert mapping.contract["[city]"] == "Paris"
    assert mapping.contract["[contract_total_amount]"] == "1000.00"
    assert mapping.completion_certificate["[certificate_amount_text]"] == "Nine hundred currency units"


def test_build_template_mapping_fills_empty_work_slots() -> None:
    payload = _payload_with_items("Only one item")
    mapping = build_template_mapping(payload)

    assert mapping.contract["[contract_work_1]"] == "Only one item"
    assert mapping.contract["[contract_work_2]"] == ""
    assert mapping.completion_certificate["[certificate_work_5]"] == ""


def test_build_template_mapping_collapses_overflow_work_items() -> None:
    payload = _payload_with_items("A", "B", "C", "D", "E", "F")
    mapping = build_template_mapping(payload)

    assert mapping.contract["[contract_work_4]"] == "D"
    assert mapping.contract["[contract_work_5]"] == "E; F"

