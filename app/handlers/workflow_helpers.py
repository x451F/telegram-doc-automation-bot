"""Shared helper functions for FSM workflow handlers."""

from __future__ import annotations

from typing import Any, Mapping

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.handlers.prompts import ask_contract_total_amount, ask_work_item
from app.services.work_items import WorkItemOption
from app.states import DocumentWorkflowStates


def get_callback_message(callback: CallbackQuery) -> Message | None:
    """Return callback message when available and compatible with Message API."""
    message = callback.message
    if isinstance(message, Message):
        return message
    return None


def get_required_work_items(data: Mapping[str, Any]) -> int:
    """Extract validated work item count from state data."""
    raw_count = data.get("work_item_count", 1)
    try:
        return max(1, int(raw_count))
    except (TypeError, ValueError):
        return 1


async def append_work_item_and_continue(
    message: Message,
    state: FSMContext,
    work_item_text: str,
    work_item_catalog: tuple[WorkItemOption, ...],
) -> None:
    """Append work item to state and route to next workflow step."""
    data = await state.get_data()
    selected_items = list(data.get("work_items", []))
    required_items = get_required_work_items(data)

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

