"""Access control helpers for admin allowlist checks."""

from __future__ import annotations

from aiogram.types import CallbackQuery, Message

from app.config import AppSettings


def is_user_allowed(user_id: int, settings: AppSettings) -> bool:
    """Return whether a user is allowed based on configured allowlist."""
    allowlist = settings.access.admin_allowlist
    if not allowlist:
        return True
    return user_id in allowlist


async def ensure_message_access(message: Message, settings: AppSettings) -> bool:
    """Validate message sender against allowlist and send denial response when needed."""
    sender = message.from_user
    if sender is None:
        return False

    if is_user_allowed(sender.id, settings):
        return True

    await message.answer("Access denied. Your account is not in the bot allowlist.")
    return False


async def ensure_callback_access(callback: CallbackQuery, settings: AppSettings) -> bool:
    """Validate callback sender against allowlist and send denial response when needed."""
    sender = callback.from_user
    if is_user_allowed(sender.id, settings):
        return True

    await callback.answer("Access denied.", show_alert=True)
    return False

