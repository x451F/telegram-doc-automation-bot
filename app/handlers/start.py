"""Initial command handlers for bot bootstrapping."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.keyboards.main_menu import build_main_menu


router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Greet the user and expose available actions."""
    await message.answer(
        text=(
            "Hello! This bot is prepared for a multi-step document workflow.\n"
            "Use the menu to continue."
        ),
        reply_markup=build_main_menu(),
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Provide short onboarding instructions."""
    await message.answer(
        "Planned features: DOCX generation from templates, optional PDF conversion, and ZIP export."
    )

