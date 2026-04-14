"""Application configuration and environment loading."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _parse_bool(raw_value: str | None, default: bool) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_extensions(raw_value: str | None) -> tuple[str, ...]:
    if not raw_value:
        return (".docx",)

    extensions: list[str] = []
    for value in raw_value.split(","):
        extension = value.strip().lower()
        if not extension:
            continue
        if not extension.startswith("."):
            extension = f".{extension}"
        extensions.append(extension)

    return tuple(extensions) if extensions else (".docx",)


@dataclass(slots=True, frozen=True)
class BotSettings:
    token: str
    parse_mode: str = "HTML"


@dataclass(slots=True, frozen=True)
class StorageSettings:
    output_dir: Path
    templates_dir: Path
    data_dir: Path


@dataclass(slots=True, frozen=True)
class DocumentSettings:
    allowed_template_extensions: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class FeatureFlags:
    enable_pdf_conversion: bool
    enable_zip_export: bool


@dataclass(slots=True, frozen=True)
class AppSettings:
    bot: BotSettings
    storage: StorageSettings
    documents: DocumentSettings
    features: FeatureFlags
    log_level: str


def load_settings(env_file: str | Path | None = ".env") -> AppSettings:
    """Load settings from environment variables and optional .env file."""
    if env_file:
        load_dotenv(dotenv_path=Path(env_file), override=False)

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is required. Provide it in the environment or .env file.")

    parse_mode = os.getenv("PARSE_MODE", "HTML")
    log_level = os.getenv("LOG_LEVEL", "INFO")

    project_root = Path.cwd()
    output_dir = Path(os.getenv("OUTPUT_DIR", project_root / "output")).resolve()
    templates_dir = Path(os.getenv("TEMPLATES_DIR", project_root / "app" / "templates")).resolve()
    data_dir = Path(os.getenv("DATA_DIR", project_root / "app" / "data")).resolve()

    allowed_extensions = _parse_extensions(os.getenv("ALLOWED_TEMPLATE_EXTENSIONS"))
    enable_pdf = _parse_bool(os.getenv("ENABLE_PDF_CONVERSION"), default=False)
    enable_zip = _parse_bool(os.getenv("ENABLE_ZIP_EXPORT"), default=True)

    return AppSettings(
        bot=BotSettings(token=token, parse_mode=parse_mode),
        storage=StorageSettings(
            output_dir=output_dir,
            templates_dir=templates_dir,
            data_dir=data_dir,
        ),
        documents=DocumentSettings(allowed_template_extensions=allowed_extensions),
        features=FeatureFlags(
            enable_pdf_conversion=enable_pdf,
            enable_zip_export=enable_zip,
        ),
        log_level=log_level,
    )

