"""Start and onboarding handlers for document intake workflow."""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import AppSettings
from app.handlers.prompts import ask_document_type, send_welcome
from app.keyboards.main_menu import build_main_menu
from app.services.access_control import ensure_message_access
from app.states import DocumentWorkflowStates


router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message, settings: AppSettings) -> None:
    """Greet user and show workflow entry controls."""
    if not await ensure_message_access(message, settings):
        return
    await send_welcome(message)


@router.message(Command("new"))
@router.message(F.text == "Start Intake Workflow")
async def handle_start_workflow(message: Message, state: FSMContext, settings: AppSettings) -> None:
    """Begin FSM flow and request document type."""
    if not await ensure_message_access(message, settings):
        return

    await state.clear()
    await state.set_state(DocumentWorkflowStates.choosing_document_type)
    await ask_document_type(message)


@router.message(Command("help"))
@router.message(F.text == "Help")
async def handle_help(message: Message, settings: AppSettings) -> None:
    """Provide concise workflow instructions."""
    if not await ensure_message_access(message, settings):
        return
    await message.answer(
        (
            "Workflow fields:\n"
            "- contract_number, contract_date\n"
            "- work item count and work_items\n"
            "- contract_total_amount, net_amount\n"
            "- certificate_number, certificate_date\n"
            "- amount_in_words\n\n"
            "Commands: /new, /cancel, /start."
        ),
        reply_markup=build_main_menu(),
    )
