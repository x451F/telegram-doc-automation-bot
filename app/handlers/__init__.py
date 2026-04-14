"""Router registry for all Telegram update handlers."""

from aiogram import Dispatcher

from app.handlers.callbacks import router as callbacks_router
from app.handlers.messages import router as messages_router
from app.handlers.navigation import router as navigation_router
from app.handlers.start import router as start_router


def register_handlers(dispatcher: Dispatcher) -> None:
    """Attach application routers to the global dispatcher."""
    dispatcher.include_router(start_router)
    dispatcher.include_router(navigation_router)
    dispatcher.include_router(callbacks_router)
    dispatcher.include_router(messages_router)
