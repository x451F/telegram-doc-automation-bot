"""Message handlers that collect typed input for each workflow state."""

from __future__ import annotations

from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import AppSettings
from app.handlers.prompts import (
    ask_amount_in_words,
    ask_certificate_date,
    ask_certificate_number,
    ask_contract_date,
    ask_contract_number,
    ask_contract_total_amount,
    ask_custom_work_item,
    ask_net_amount,
    ask_work_item,
    ask_work_item_count,
    show_payload_review,
)
from app.services.access_control import ensure_message_access
from app.services.payloads import build_payload
from app.services.validation import (
    parse_date_input,
    parse_decimal_amount,
    parse_non_empty_text,
    parse_positive_int,
)
from app.services.work_items import WorkItemOption
from app.states import DocumentWorkflowStates


router = Router(name="messages")


def _get_required_work_items(data: dict[str, Any]) -> int:
    raw_count = data.get("work_item_count", 1)
    try:
        return max(1, int(raw_count))
    except (TypeError, ValueError):
        return 1


async def _append_work_item_and_continue(
    message: Message,
    state: FSMContext,
    work_item_text: str,
    work_item_catalog: tuple[WorkItemOption, ...],
) -> None:
    data = await state.get_data()
    selected_items = list(data.get("work_items", []))
    required_items = _get_required_work_items(data)

    selected_items.append(work_item_text)
    await state.update_data(work_items=selected_items)

    if len(selected_items) >= required_items:
        await state.set_state(DocumentWorkflowStates.entering_contract_total_amount)
        await ask_contract_total_amount(message)
        return

    await state.set_state(DocumentWorkflowStates.choosing_work_item)
    await ask_work_item(
        message=message,
        options=work_item_catalog,
        selected_count=len(selected_items),
        required_count=required_items,
    )


@router.message(DocumentWorkflowStates.choosing_document_type)
async def handle_message_while_choosing_document_type(
    message: Message, settings: AppSettings
) -> None:
    """Prompt user to use inline options for document type selection."""
    if not await ensure_message_access(message, settings):
        return
    await message.answer("Choose document type using the inline buttons below.")


@router.message(DocumentWorkflowStates.entering_contract_number, F.text)
async def handle_contract_number(
    message: Message,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Collect contract_number from text input."""
    if not await ensure_message_access(message, settings):
        return
    try:
        value = parse_non_empty_text(message.text or "", "contract_number")
    except ValueError as exc:
        await message.answer(str(exc))
        await ask_contract_number(message)
        return

    await state.update_data(contract_number=value)
    await state.set_state(DocumentWorkflowStates.entering_contract_date)
    await ask_contract_date(message)


@router.message(DocumentWorkflowStates.entering_contract_date, F.text)
async def handle_contract_date(
    message: Message,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Collect contract_date from text input."""
    if not await ensure_message_access(message, settings):
        return
    try:
        value = parse_date_input(message.text or "", "contract_date")
    except ValueError as exc:
        await message.answer(str(exc))
        await ask_contract_date(message)
        return

    await state.update_data(contract_date=value)
    await state.set_state(DocumentWorkflowStates.entering_work_item_count)
    await ask_work_item_count(message)


@router.message(DocumentWorkflowStates.entering_work_item_count, F.text)
async def handle_work_item_count(
    message: Message,
    state: FSMContext,
    settings: AppSettings,
    work_item_catalog: tuple[WorkItemOption, ...],
) -> None:
    """Collect work item count from text input."""
    if not await ensure_message_access(message, settings):
        return
    try:
        value = parse_positive_int(message.text or "", "work item count")
    except ValueError as exc:
        await message.answer(str(exc))
        await ask_work_item_count(message)
        return

    await state.update_data(work_item_count=value, work_items=[])
    await state.set_state(DocumentWorkflowStates.choosing_work_item)
    await ask_work_item(
        message=message,
        options=work_item_catalog,
        selected_count=0,
        required_count=value,
    )


@router.message(DocumentWorkflowStates.choosing_work_item, F.text)
async def handle_work_item_text(
    message: Message,
    state: FSMContext,
    settings: AppSettings,
    work_item_catalog: tuple[WorkItemOption, ...],
) -> None:
    """Allow custom work item input directly in selection state."""
    if not await ensure_message_access(message, settings):
        return
    try:
        value = parse_non_empty_text(message.text or "", "work item")
    except ValueError as exc:
        await message.answer(str(exc))
        return

    await _append_work_item_and_continue(
        message=message,
        state=state,
        work_item_text=value,
        work_item_catalog=work_item_catalog,
    )


@router.message(DocumentWorkflowStates.entering_custom_work_item, F.text)
async def handle_custom_work_item(
    message: Message,
    state: FSMContext,
    settings: AppSettings,
    work_item_catalog: tuple[WorkItemOption, ...],
) -> None:
    """Collect custom work item text after custom option callback."""
    if not await ensure_message_access(message, settings):
        return
    try:
        value = parse_non_empty_text(message.text or "", "work item")
    except ValueError as exc:
        await message.answer(str(exc))
        await ask_custom_work_item(message)
        return

    await _append_work_item_and_continue(
        message=message,
        state=state,
        work_item_text=value,
        work_item_catalog=work_item_catalog,
    )


@router.message(DocumentWorkflowStates.entering_contract_total_amount, F.text)
async def handle_contract_total_amount(
    message: Message,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Collect contract total amount from text input."""
    if not await ensure_message_access(message, settings):
        return
    try:
        value = parse_decimal_amount(message.text or "", "contract_total_amount")
    except ValueError as exc:
        await message.answer(str(exc))
        await ask_contract_total_amount(message)
        return

    await state.update_data(contract_total_amount=f"{value:.2f}")
    await state.set_state(DocumentWorkflowStates.entering_net_amount)
    await ask_net_amount(message)


@router.message(DocumentWorkflowStates.entering_net_amount, F.text)
async def handle_net_amount(
    message: Message,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Collect net amount from text input."""
    if not await ensure_message_access(message, settings):
        return
    try:
        value = parse_decimal_amount(message.text or "", "net_amount")
    except ValueError as exc:
        await message.answer(str(exc))
        await ask_net_amount(message)
        return

    await state.update_data(net_amount=f"{value:.2f}")
    await state.set_state(DocumentWorkflowStates.entering_certificate_number)
    await ask_certificate_number(message)


@router.message(DocumentWorkflowStates.entering_certificate_number, F.text)
async def handle_certificate_number(
    message: Message,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Collect certificate number from text input."""
    if not await ensure_message_access(message, settings):
        return
    try:
        value = parse_non_empty_text(message.text or "", "certificate_number")
    except ValueError as exc:
        await message.answer(str(exc))
        await ask_certificate_number(message)
        return

    await state.update_data(certificate_number=value)
    await state.set_state(DocumentWorkflowStates.entering_certificate_date)
    await ask_certificate_date(message)


@router.message(DocumentWorkflowStates.entering_certificate_date, F.text)
async def handle_certificate_date(
    message: Message,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Collect certificate date from text input."""
    if not await ensure_message_access(message, settings):
        return
    try:
        value = parse_date_input(message.text or "", "certificate_date")
    except ValueError as exc:
        await message.answer(str(exc))
        await ask_certificate_date(message)
        return

    await state.update_data(certificate_date=value)
    await state.set_state(DocumentWorkflowStates.entering_amount_in_words)
    await ask_amount_in_words(message)


@router.message(DocumentWorkflowStates.entering_amount_in_words, F.text)
async def handle_amount_in_words(
    message: Message,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Collect amount in words and move to review step."""
    if not await ensure_message_access(message, settings):
        return
    try:
        value = parse_non_empty_text(message.text or "", "amount_in_words")
    except ValueError as exc:
        await message.answer(str(exc))
        await ask_amount_in_words(message)
        return

    await state.update_data(amount_in_words=value)
    data = await state.get_data()
    payload = build_payload(data)
    await state.set_state(DocumentWorkflowStates.reviewing_payload)
    await show_payload_review(message, payload)


@router.message(DocumentWorkflowStates.reviewing_payload, F.text)
async def handle_review_message(
    message: Message, settings: AppSettings
) -> None:
    """Guide user to submit/back actions during review state."""
    if not await ensure_message_access(message, settings):
        return
    await message.answer("Use inline buttons: Submit payload, Back, or Cancel.")
