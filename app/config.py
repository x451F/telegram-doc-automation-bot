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


def _parse_int_set(raw_value: str | None) -> frozenset[int]:
    if not raw_value:
        return frozenset()

    values: set[int] = set()
    for chunk in raw_value.split(","):
        candidate = chunk.strip()
        if not candidate:
            continue
        try:
            values.add(int(candidate))
        except ValueError:
            continue
    return frozenset(values)


@dataclass(slots=True, frozen=True)
class BotSettings:
    token: str
    parse_mode: str = "HTML"


@dataclass(slots=True, frozen=True)
class StorageSettings:
    output_dir: Path
    templates_dir: Path
    data_dir: Path
    work_items_file: Path
    working_dir_prefix: str


@dataclass(slots=True, frozen=True)
class DocumentSettings:
    allowed_template_extensions: tuple[str, ...]
    default_city: str


@dataclass(slots=True, frozen=True)
class FeatureFlags:
    enable_pdf_conversion: bool
    enable_zip_export: bool
    pdf_backend: str
    cleanup_temp_files: bool


@dataclass(slots=True, frozen=True)
class AccessSettings:
    admin_allowlist: frozenset[int]


@dataclass(slots=True, frozen=True)
class AppSettings:
    bot: BotSettings
    storage: StorageSettings
    documents: DocumentSettings
    features: FeatureFlags
    access: AccessSettings
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
    work_items_file = Path(
        os.getenv("WORK_ITEMS_FILE", project_root / "app" / "data" / "work_items.example.json")
    ).resolve()
    working_dir_prefix = os.getenv("WORKING_DIR_PREFIX", "job")

    allowed_extensions = _parse_extensions(os.getenv("ALLOWED_TEMPLATE_EXTENSIONS"))
    default_city = os.getenv("DEFAULT_CITY", "Sample City")
    enable_pdf = _parse_bool(os.getenv("ENABLE_PDF_CONVERSION"), default=False)
    enable_zip = _parse_bool(os.getenv("ENABLE_ZIP_EXPORT"), default=True)
    pdf_backend = os.getenv("PDF_BACKEND", "auto")
    cleanup_temp_files = _parse_bool(os.getenv("CLEANUP_TEMP_FILES"), default=True)
    admin_allowlist = _parse_int_set(os.getenv("ADMIN_ALLOWLIST"))

    return AppSettings(
        bot=BotSettings(token=token, parse_mode=parse_mode),
        storage=StorageSettings(
            output_dir=output_dir,
            templates_dir=templates_dir,
            data_dir=data_dir,
            work_items_file=work_items_file,
            working_dir_prefix=working_dir_prefix,
        ),
        documents=DocumentSettings(
            allowed_template_extensions=allowed_extensions,
            default_city=default_city,
        ),
        features=FeatureFlags(
            enable_pdf_conversion=enable_pdf,
            enable_zip_export=enable_zip,
            pdf_backend=pdf_backend,
            cleanup_temp_files=cleanup_temp_files,
        ),
        access=AccessSettings(admin_allowlist=admin_allowlist),
        log_level=log_level,
    )
