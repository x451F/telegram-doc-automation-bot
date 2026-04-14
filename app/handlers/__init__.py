"""Router registry for all Telegram update handlers."""

from aiogram import Dispatcher

from app.handlers.start import router as start_router


def register_handlers(dispatcher: Dispatcher) -> None:
    """Attach application routers to the global dispatcher."""
    dispatcher.include_router(start_router)

