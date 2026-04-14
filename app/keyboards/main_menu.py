"""Main menu keyboard for the initial workflow actions."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def build_main_menu() -> ReplyKeyboardMarkup:
    """Return a reply keyboard with workflow entry actions."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Start Intake Workflow")],
            [KeyboardButton(text="Cancel Workflow")],
            [KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )
