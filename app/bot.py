"""Bot entrypoint and aiogram application bootstrap."""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from app.config import load_settings
from app.handlers import register_handlers
from app.services.file_service import ensure_directory
from app.services.work_items import load_work_items_catalog


logger = logging.getLogger(__name__)


def configure_logging(log_level: str) -> None:
    """Configure process-wide structured logging."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format=(
            "ts=%(asctime)s "
            "level=%(levelname)s "
            "logger=%(name)s "
            "message=%(message)s"
        ),
        stream=sys.stdout,
    )


async def run_bot() -> None:
    """Load configuration, wire routers, and start long polling."""
    settings = load_settings()
    configure_logging(settings.log_level)

    await ensure_directory(settings.storage.output_dir)
    await ensure_directory(settings.storage.templates_dir)
    await ensure_directory(settings.storage.data_dir)
    work_item_catalog = load_work_items_catalog(settings.storage.work_items_file)
    logger.info("Loaded %d work item options.", len(work_item_catalog))

    parse_mode = ParseMode(settings.bot.parse_mode)
    bot = Bot(
        token=settings.bot.token,
        default=DefaultBotProperties(parse_mode=parse_mode),
    )
    dispatcher = Dispatcher()
    register_handlers(dispatcher)

    logger.info("Starting Telegram bot polling.")
    await dispatcher.start_polling(
        bot,
        settings=settings,
        work_item_catalog=work_item_catalog,
    )


def main() -> None:
    """Synchronous entrypoint for CLI and script execution."""
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user request.")


if __name__ == "__main__":
    main()
