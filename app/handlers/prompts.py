"""Prompt helpers to keep message/callback handlers focused on flow logic."""

from __future__ import annotations

from datetime import date

from aiogram.types import Message

from app.keyboards.main_menu import build_main_menu
from app.keyboards.workflow import (
    build_amount_presets_keyboard,
    build_back_keyboard,
    build_certificate_number_presets_keyboard,
    build_contract_number_presets_keyboard,
    build_day_picker_keyboard,
    build_document_type_keyboard,
    build_review_keyboard,
    build_work_count_keyboard,
    build_work_item_selection_keyboard,
)
from app.services.payloads import DocumentIntakePayload, format_payload_summary
from app.services.work_items import WorkItemOption


async def send_welcome(message: Message) -> None:
    """Send initial greeting and expose the workflow entry point."""
    await message.answer(
        (
            "Welcome to the document workflow bot.\n"
            "Use the menu to start collecting fields for a service agreement or completion certificate."
        ),
        reply_markup=build_main_menu(),
    )


async def ask_document_type(message: Message) -> None:
    """Prompt user to choose a document category."""
    await message.answer(
        "Choose a document type to begin.",
        reply_markup=build_document_type_keyboard(),
    )


async def ask_contract_number(message: Message) -> None:
    """Prompt for contract number with optional presets."""
    await message.answer(
        "Enter `contract_number` or choose a preset.",
        reply_markup=build_contract_number_presets_keyboard(),
    )


async def ask_contract_date(message: Message) -> None:
    """Prompt for contract date with a day picker helper."""
    current_month = date.today().strftime("%Y-%m")
    await message.answer(
        (
            "Enter `contract_date` in YYYY-MM-DD, DD.MM.YYYY, or DD/MM/YYYY.\n"
            f"Or pick a day to apply in the current month ({current_month})."
        ),
        reply_markup=build_day_picker_keyboard(),
    )


async def ask_work_item_count(message: Message) -> None:
    """Prompt for the number of work items."""
    await message.answer(
        "Enter the number of `work_items` (1-20) or choose a quick value.",
        reply_markup=build_work_count_keyboard(),
    )


async def ask_work_item(
    message: Message,
    options: tuple[WorkItemOption, ...],
    selected_count: int,
    required_count: int,
) -> None:
    """Prompt for the next work item selection or custom value."""
    await message.answer(
        (
            f"Select work item {selected_count + 1} of {required_count}.\n"
            "You can choose a catalog option or tap Custom work item."
        ),
        reply_markup=build_work_item_selection_keyboard(options),
    )


async def ask_custom_work_item(message: Message) -> None:
    """Prompt user to enter custom work item text."""
    await message.answer(
        "Enter custom text for this work item.",
        reply_markup=build_back_keyboard(),
    )


async def ask_contract_total_amount(message: Message) -> None:
    """Prompt for contract total amount."""
    await message.answer(
        "Enter `contract_total_amount` (for example: 12500.00) or choose a preset.",
        reply_markup=build_amount_presets_keyboard(),
    )


async def ask_net_amount(message: Message) -> None:
    """Prompt for net amount."""
    await message.answer(
        "Enter `net_amount` (for example: 10416.67) or choose a preset.",
        reply_markup=build_amount_presets_keyboard(),
    )


async def ask_certificate_number(message: Message) -> None:
    """Prompt for certificate number with optional presets."""
    await message.answer(
        "Enter `certificate_number` or choose a preset.",
        reply_markup=build_certificate_number_presets_keyboard(),
    )


async def ask_certificate_date(message: Message) -> None:
    """Prompt for certificate date with day picker helper."""
    current_month = date.today().strftime("%Y-%m")
    await message.answer(
        (
            "Enter `certificate_date` in YYYY-MM-DD, DD.MM.YYYY, or DD/MM/YYYY.\n"
            f"Or pick a day to apply in the current month ({current_month})."
        ),
        reply_markup=build_day_picker_keyboard(),
    )


async def ask_amount_in_words(message: Message) -> None:
    """Prompt for amount in words."""
    await message.answer(
        "Enter `amount_in_words` in plain English text.",
        reply_markup=build_back_keyboard(),
    )


async def show_payload_review(message: Message, payload: DocumentIntakePayload) -> None:
    """Show final payload summary with submit/back controls."""
    await message.answer(
        format_payload_summary(payload),
        reply_markup=build_review_keyboard(),
    )

