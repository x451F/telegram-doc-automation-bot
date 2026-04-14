"""Navigation handlers for cancel/back actions in the FSM flow."""

from __future__ import annotations

from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
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
    ask_document_type,
    ask_net_amount,
    ask_work_item,
    ask_work_item_count,
)
from app.keyboards.main_menu import build_main_menu
from app.keyboards.workflow import NAV_BACK, NAV_CANCEL
from app.services.access_control import ensure_callback_access, ensure_message_access
from app.services.work_items import WorkItemOption
from app.states import DocumentWorkflowStates


router = Router(name="navigation")


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


async def _navigate_back(
    message: Message,
    state: FSMContext,
    work_item_catalog: tuple[WorkItemOption, ...],
) -> None:
    current_state = await state.get_state()
    data = await state.get_data()

    if current_state is None:
        await message.answer("No active workflow. Use /new to start.", reply_markup=build_main_menu())
        return

    if current_state == DocumentWorkflowStates.choosing_document_type.state:
        await message.answer("You are already at the first step.")
        return

    if current_state == DocumentWorkflowStates.entering_contract_number.state:
        await state.set_state(DocumentWorkflowStates.choosing_document_type)
        await ask_document_type(message)
        return

    if current_state == DocumentWorkflowStates.entering_contract_date.state:
        await state.set_state(DocumentWorkflowStates.entering_contract_number)
        await ask_contract_number(message)
        return

    if current_state == DocumentWorkflowStates.entering_work_item_count.state:
        await state.set_state(DocumentWorkflowStates.entering_contract_date)
        await ask_contract_date(message)
        return

    if current_state == DocumentWorkflowStates.choosing_work_item.state:
        selected_items = list(data.get("work_items", []))
        if selected_items:
            removed_item = selected_items.pop()
            await state.update_data(work_items=selected_items)
            await message.answer(f"Removed: {removed_item}")
            required_items = _get_required_work_items(data)
            await ask_work_item(
                message=message,
                options=work_item_catalog,
                selected_count=len(selected_items),
                required_count=required_items,
            )
            return

        await state.set_state(DocumentWorkflowStates.entering_work_item_count)
        await ask_work_item_count(message)
        return

    if current_state == DocumentWorkflowStates.entering_custom_work_item.state:
        await state.set_state(DocumentWorkflowStates.choosing_work_item)
        required_items = _get_required_work_items(data)
        selected_items = list(data.get("work_items", []))
        await ask_work_item(
            message=message,
            options=work_item_catalog,
            selected_count=len(selected_items),
            required_count=required_items,
        )
        return

    if current_state == DocumentWorkflowStates.entering_contract_total_amount.state:
        selected_items = list(data.get("work_items", []))
        if selected_items:
            selected_items.pop()
            await state.update_data(work_items=selected_items)
        await state.set_state(DocumentWorkflowStates.choosing_work_item)
        required_items = _get_required_work_items(data)
        await ask_work_item(
            message=message,
            options=work_item_catalog,
            selected_count=len(selected_items),
            required_count=required_items,
        )
        return

    if current_state == DocumentWorkflowStates.entering_net_amount.state:
        await state.set_state(DocumentWorkflowStates.entering_contract_total_amount)
        await ask_contract_total_amount(message)
        return

    if current_state == DocumentWorkflowStates.entering_certificate_number.state:
        await state.set_state(DocumentWorkflowStates.entering_net_amount)
        await ask_net_amount(message)
        return

    if current_state == DocumentWorkflowStates.entering_certificate_date.state:
        await state.set_state(DocumentWorkflowStates.entering_certificate_number)
        await ask_certificate_number(message)
        return

    if current_state == DocumentWorkflowStates.entering_amount_in_words.state:
        await state.set_state(DocumentWorkflowStates.entering_certificate_date)
        await ask_certificate_date(message)
        return

    if current_state == DocumentWorkflowStates.reviewing_payload.state:
        await state.set_state(DocumentWorkflowStates.entering_amount_in_words)
        await ask_amount_in_words(message)
        return


@router.message(Command("cancel"))
@router.message(F.text == "Cancel Workflow")
async def handle_cancel_message(message: Message, state: FSMContext, settings: AppSettings) -> None:
    """Cancel active workflow and clear FSM data."""
    if not await ensure_message_access(message, settings):
        return
    await state.clear()
    await message.answer("Workflow cancelled.", reply_markup=build_main_menu())


@router.callback_query(F.data == NAV_CANCEL)
async def handle_cancel_callback(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
) -> None:
    """Cancel flow via inline callback."""
    if not await ensure_callback_access(callback, settings):
        return
    await callback.answer()
    await state.clear()
    message = _get_callback_message(callback)
    if message is not None:
        await message.answer("Workflow cancelled.", reply_markup=build_main_menu())


@router.callback_query(F.data == NAV_BACK)
async def handle_back_callback(
    callback: CallbackQuery,
    state: FSMContext,
    settings: AppSettings,
    work_item_catalog: tuple[WorkItemOption, ...],
) -> None:
    """Step back to previous part of the intake flow."""
    if not await ensure_callback_access(callback, settings):
        return
    await callback.answer()
    message = _get_callback_message(callback)
    if message is None:
        return
    await _navigate_back(message=message, state=state, work_item_catalog=work_item_catalog)
