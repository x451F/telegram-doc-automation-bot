"""Reusable inline keyboards for document intake workflow steps."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.services.work_items import WorkItemOption


NAV_BACK = "nav:back"
NAV_CANCEL = "nav:cancel"
NAV_SUBMIT = "nav:submit"

DOC_TYPE_SERVICE_AGREEMENT = "doc:service_agreement"
DOC_TYPE_COMPLETION_CERTIFICATE = "doc:completion_certificate"

WORK_COUNT_PREFIX = "work_count:"
WORK_ITEM_PREFIX = "work_item:"
WORK_ITEM_CUSTOM = "work_item:custom"
CONTRACT_PRESET_PREFIX = "contract_preset:"
CERTIFICATE_PRESET_PREFIX = "certificate_preset:"
AMOUNT_PRESET_PREFIX = "amount_preset:"
DAY_PICKER_PREFIX = "day_picker:"


CONTRACT_NUMBER_PRESETS: tuple[str, ...] = (
    "AGR-2026-001",
    "AGR-2026-002",
    "AGR-2026-003",
)

CERTIFICATE_NUMBER_PRESETS: tuple[str, ...] = (
    "CERT-2026-001",
    "CERT-2026-002",
    "CERT-2026-003",
)

AMOUNT_PRESETS: tuple[Decimal, ...] = (
    Decimal("1000.00"),
    Decimal("5000.00"),
    Decimal("10000.00"),
    Decimal("25000.00"),
)


def _back_cancel_row() -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(text="Back", callback_data=NAV_BACK),
        InlineKeyboardButton(text="Cancel", callback_data=NAV_CANCEL),
    ]


def build_document_type_keyboard() -> InlineKeyboardMarkup:
    """Build document type selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Service Agreement",
                    callback_data=DOC_TYPE_SERVICE_AGREEMENT,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Completion Certificate",
                    callback_data=DOC_TYPE_COMPLETION_CERTIFICATE,
                )
            ],
            _back_cancel_row(),
        ]
    )


def build_back_keyboard() -> InlineKeyboardMarkup:
    """Build a minimal navigation keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[_back_cancel_row()])


def build_contract_number_presets_keyboard() -> InlineKeyboardMarkup:
    """Build contract number presets keyboard."""
    rows = [
        [InlineKeyboardButton(text=preset, callback_data=f"{CONTRACT_PRESET_PREFIX}{preset}")]
        for preset in CONTRACT_NUMBER_PRESETS
    ]
    rows.append(_back_cancel_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_certificate_number_presets_keyboard() -> InlineKeyboardMarkup:
    """Build certificate number presets keyboard."""
    rows = [
        [InlineKeyboardButton(text=preset, callback_data=f"{CERTIFICATE_PRESET_PREFIX}{preset}")]
        for preset in CERTIFICATE_NUMBER_PRESETS
    ]
    rows.append(_back_cancel_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_work_count_keyboard() -> InlineKeyboardMarkup:
    """Build numeric choices for number of work items."""
    rows: list[list[InlineKeyboardButton]] = []
    for start in (1, 4):
        row: list[InlineKeyboardButton] = []
        for value in range(start, start + 3):
            row.append(
                InlineKeyboardButton(text=str(value), callback_data=f"{WORK_COUNT_PREFIX}{value}")
            )
        rows.append(row)
    rows.append(_back_cancel_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_work_item_selection_keyboard(
    options: tuple[WorkItemOption, ...],
) -> InlineKeyboardMarkup:
    """Build selectable work item options with custom input fallback."""
    rows: list[list[InlineKeyboardButton]] = []
    for index, option in enumerate(options):
        rows.append(
            [InlineKeyboardButton(text=option.label, callback_data=f"{WORK_ITEM_PREFIX}{index}")]
        )

    rows.append([InlineKeyboardButton(text="Custom work item", callback_data=WORK_ITEM_CUSTOM)])
    rows.append(_back_cancel_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_day_picker_keyboard() -> InlineKeyboardMarkup:
    """Build a day picker using current month and year."""
    rows: list[list[InlineKeyboardButton]] = []
    for start in range(1, 31, 5):
        row: list[InlineKeyboardButton] = []
        for day in range(start, min(start + 5, 32)):
            row.append(
                InlineKeyboardButton(
                    text=f"{day:02d}",
                    callback_data=f"{DAY_PICKER_PREFIX}{day:02d}",
                )
            )
        rows.append(row)

    today = date.today()
    rows.append(
        [
            InlineKeyboardButton(
                text=f"Use today ({today.isoformat()})",
                callback_data=f"{DAY_PICKER_PREFIX}today",
            )
        ]
    )
    rows.append(_back_cancel_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_amount_presets_keyboard() -> InlineKeyboardMarkup:
    """Build amount presets keyboard for monetary fields."""
    rows = [
        [
            InlineKeyboardButton(
                text=f"{amount:.2f}",
                callback_data=f"{AMOUNT_PRESET_PREFIX}{amount:.2f}",
            )
        ]
        for amount in AMOUNT_PRESETS
    ]
    rows.append(_back_cancel_row())
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_review_keyboard() -> InlineKeyboardMarkup:
    """Build review actions keyboard for final payload confirmation."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Submit payload", callback_data=NAV_SUBMIT)],
            _back_cancel_row(),
        ]
    )

