"""Callback query handlers for presets and inline workflow controls."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

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
)
from app.keyboards.main_menu import build_main_menu
from app.keyboards.workflow import (
    AMOUNT_PRESET_PREFIX,
    CERTIFICATE_PRESET_PREFIX,
    CONTRACT_PRESET_PREFIX,
    DAY_PICKER_PREFIX,
    DOC_TYPE_COMPLETION_CERTIFICATE,
    DOC_TYPE_SERVICE_AGREEMENT,
    NAV_SUBMIT,
    WORK_COUNT_PREFIX,
    WORK_ITEM_CUSTOM,
    WORK_ITEM_PREFIX,
)
from app.services.access_control import ensure_callback_access
from app.services.payloads import build_payload
from app.services.validation import parse_date_input, parse_decimal_amount, parse_non_empty_text
from app.services.work_items import WorkItemOption
from app.states import DocumentWorkflowStates


logger = logging.getLogger(__name__)
router = Router(name="callbacks")


def _get_callback_message(callback: CallbackQuery) -> Message | None:
    message = callback.message
    if isinstance(message, Message):
        return message
    return None


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


@router.callback_query(
    F.data.in_(
        {
            DOC_TYPE_SERVICE_AGREEMENT,
            DOC_TYPE_COMPLETION_CERTIFICATE,
        }
    )
)
async def handle_document_type_callback(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Handle document type selection."""
    if not await ensure_callback_access(callback, settings):
        return

    current_state = await state.get_state()
    if current_state != DocumentWorkflowStates.choosing_document_type.state:
        await callback.answer("Use /new to start a workflow.", show_alert=True)
        return

    payload = callback.data or ""
    document_type = (
        "service_agreement"
        if payload == DOC_TYPE_SERVICE_AGREEMENT
        else "completion_certificate"
    )
    await state.update_data(document_type=document_type)
    await state.set_state(DocumentWorkflowStates.entering_contract_number)
    await callback.answer("Document type selected.")

    message = _get_callback_message(callback)
    if message is not None:
        await ask_contract_number(message)


@router.callback_query(F.data.startswith(CONTRACT_PRESET_PREFIX))
async def handle_contract_number_preset(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Apply contract number preset and continue workflow."""
    if not await ensure_callback_access(callback, settings):
        return

    if await state.get_state() != DocumentWorkflowStates.entering_contract_number.state:
        await callback.answer("Contract number is not expected at this step.", show_alert=True)
        return

    payload = callback.data or ""
    value = payload.removeprefix(CONTRACT_PRESET_PREFIX)
    try:
        contract_number = parse_non_empty_text(value, "contract_number")
    except ValueError:
        await callback.answer("Invalid preset value.", show_alert=True)
        return

    await state.update_data(contract_number=contract_number)
    await state.set_state(DocumentWorkflowStates.entering_contract_date)
    await callback.answer("Contract number selected.")

    message = _get_callback_message(callback)
    if message is not None:
        await ask_contract_date(message)


@router.callback_query(F.data.startswith(DAY_PICKER_PREFIX))
async def handle_day_picker_callback(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Apply day-picker value for contract/certificate date fields."""
    if not await ensure_callback_access(callback, settings):
        return

    current_state = await state.get_state()
    if current_state not in {
        DocumentWorkflowStates.entering_contract_date.state,
        DocumentWorkflowStates.entering_certificate_date.state,
    }:
        await callback.answer("Date is not expected at this step.", show_alert=True)
        return

    payload = callback.data or ""
    token = payload.removeprefix(DAY_PICKER_PREFIX)
    if token == "today":
        value = date.today().isoformat()
    else:
        try:
            day = int(token)
            now = date.today()
            picked = date(now.year, now.month, day)
            value = picked.isoformat()
        except ValueError:
            await callback.answer("Invalid day selected for current month.", show_alert=True)
            return

    field_name = (
        "contract_date"
        if current_state == DocumentWorkflowStates.entering_contract_date.state
        else "certificate_date"
    )
    try:
        parsed = parse_date_input(value, field_name)
    except ValueError:
        await callback.answer("Invalid date value.", show_alert=True)
        return

    await state.update_data(**{field_name: parsed})
    await callback.answer("Date selected.")

    message = _get_callback_message(callback)
    if message is None:
        return

    if current_state == DocumentWorkflowStates.entering_contract_date.state:
        await state.set_state(DocumentWorkflowStates.entering_work_item_count)
        await ask_work_item_count(message)
        return

    await state.set_state(DocumentWorkflowStates.entering_amount_in_words)
    await ask_amount_in_words(message)


@router.callback_query(F.data.startswith(WORK_COUNT_PREFIX))
async def handle_work_count_callback(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
    work_item_catalog: tuple[WorkItemOption, ...],
) -> None:
    """Apply work item count preset and continue to item selection."""
    if not await ensure_callback_access(callback, settings):
        return

    if await state.get_state() != DocumentWorkflowStates.entering_work_item_count.state:
        await callback.answer("Work item count is not expected now.", show_alert=True)
        return

    payload = callback.data or ""
    value = payload.removeprefix(WORK_COUNT_PREFIX)
    try:
        count = int(value)
    except ValueError:
        await callback.answer("Invalid work item count.", show_alert=True)
        return

    if count < 1 or count > 20:
        await callback.answer("Work item count must be between 1 and 20.", show_alert=True)
        return

    await state.update_data(work_item_count=count, work_items=[])
    await state.set_state(DocumentWorkflowStates.choosing_work_item)
    await callback.answer("Work item count selected.")

    message = _get_callback_message(callback)
    if message is not None:
        await ask_work_item(
            message=message,
            options=work_item_catalog,
            selected_count=0,
            required_count=count,
        )


@router.callback_query(F.data == WORK_ITEM_CUSTOM)
async def handle_work_item_custom_callback(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Switch to custom work item text input."""
    if not await ensure_callback_access(callback, settings):
        return

    if await state.get_state() != DocumentWorkflowStates.choosing_work_item.state:
        await callback.answer("Work item is not expected now.", show_alert=True)
        return

    await callback.answer("Enter custom work item.")
    await state.set_state(DocumentWorkflowStates.entering_custom_work_item)
    message = _get_callback_message(callback)
    if message is not None:
        await ask_custom_work_item(message)


@router.callback_query(F.data.startswith(WORK_ITEM_PREFIX))
async def handle_work_item_callback(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
    work_item_catalog: tuple[WorkItemOption, ...],
) -> None:
    """Apply selected work item from dynamic catalog."""
    if not await ensure_callback_access(callback, settings):
        return

    if await state.get_state() != DocumentWorkflowStates.choosing_work_item.state:
        await callback.answer("Work item is not expected now.", show_alert=True)
        return

    payload = callback.data or ""
    raw_index = payload.removeprefix(WORK_ITEM_PREFIX)
    if raw_index == "custom":
        return

    try:
        index = int(raw_index)
    except ValueError:
        await callback.answer("Invalid work item selection.", show_alert=True)
        return

    if index < 0 or index >= len(work_item_catalog):
        await callback.answer("Work item index is out of range.", show_alert=True)
        return

    selected_option = work_item_catalog[index]
    await callback.answer("Work item selected.")

    message = _get_callback_message(callback)
    if message is None:
        return

    await _append_work_item_and_continue(
        message=message,
        state=state,
        work_item_text=selected_option.label,
        work_item_catalog=work_item_catalog,
    )


@router.callback_query(F.data.startswith(AMOUNT_PRESET_PREFIX))
async def handle_amount_preset_callback(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Apply amount preset for total/net amount states."""
    if not await ensure_callback_access(callback, settings):
        return

    current_state = await state.get_state()
    if current_state not in {
        DocumentWorkflowStates.entering_contract_total_amount.state,
        DocumentWorkflowStates.entering_net_amount.state,
    }:
        await callback.answer("Amount is not expected now.", show_alert=True)
        return

    payload = callback.data or ""
    raw_amount = payload.removeprefix(AMOUNT_PRESET_PREFIX)
    try:
        amount = parse_decimal_amount(raw_amount, "amount")
    except ValueError:
        await callback.answer("Invalid amount preset.", show_alert=True)
        return

    message = _get_callback_message(callback)
    if message is None:
        return

    if current_state == DocumentWorkflowStates.entering_contract_total_amount.state:
        await state.update_data(contract_total_amount=f"{amount:.2f}")
        await state.set_state(DocumentWorkflowStates.entering_net_amount)
        await callback.answer("Contract total amount selected.")
        await ask_net_amount(message)
        return

    await state.update_data(net_amount=f"{amount:.2f}")
    await state.set_state(DocumentWorkflowStates.entering_certificate_number)
    await callback.answer("Net amount selected.")
    await ask_certificate_number(message)


@router.callback_query(F.data.startswith(CERTIFICATE_PRESET_PREFIX))
async def handle_certificate_number_preset(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Apply certificate number preset and continue."""
    if not await ensure_callback_access(callback, settings):
        return

    if await state.get_state() != DocumentWorkflowStates.entering_certificate_number.state:
        await callback.answer("Certificate number is not expected now.", show_alert=True)
        return

    payload = callback.data or ""
    value = payload.removeprefix(CERTIFICATE_PRESET_PREFIX)
    try:
        certificate_number = parse_non_empty_text(value, "certificate_number")
    except ValueError:
        await callback.answer("Invalid preset value.", show_alert=True)
        return

    await state.update_data(certificate_number=certificate_number)
    await state.set_state(DocumentWorkflowStates.entering_certificate_date)
    await callback.answer("Certificate number selected.")

    message = _get_callback_message(callback)
    if message is not None:
        await ask_certificate_date(message)


@router.callback_query(F.data == NAV_SUBMIT)
async def handle_submit_payload_callback(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Finalize payload collection and clear state."""
    if not await ensure_callback_access(callback, settings):
        return

    if await state.get_state() != DocumentWorkflowStates.reviewing_payload.state:
        await callback.answer("Payload cannot be submitted at this step.", show_alert=True)
        return

    data = await state.get_data()
    payload = build_payload(data)
    logger.info("Collected payload submitted for document_type=%s", payload.document_type)
    await state.clear()
    await callback.answer("Payload submitted.")

    message = _get_callback_message(callback)
    if message is not None:
        await message.answer(
            "Payload collected successfully. Document generation can be plugged in next.",
            reply_markup=build_main_menu(),
        )
