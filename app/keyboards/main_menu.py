"""Main menu keyboard for the initial workflow actions."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def build_main_menu() -> ReplyKeyboardMarkup:
    """Return a small default keyboard for the first milestone."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Create Document")],
            [KeyboardButton(text="Help")],
        ],
        resize_keyboard=True,
    )

