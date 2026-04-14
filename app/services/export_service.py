"""Orchestration service for DOCX/PDF/ZIP artifact preparation."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path

from app.config import AppSettings
from app.services.archive_service import create_archive
from app.services.document_generator import (
    DocumentGenerationError,
    GeneratedDocumentPaths,
    generate_documents,
)
from app.services.file_service import create_temporary_working_directory, remove_path
from app.services.payloads import DocumentIntakePayload
from app.services.pdf_converter import convert_documents_to_pdf
from app.services.text_utils import safe_filename


logger = logging.getLogger(__name__)


class ExportPreparationError(RuntimeError):
    """Raised when core export preparation fails."""


@dataclass(slots=True, frozen=True)
class ExportBundle:
    """All artifacts prepared for Telegram delivery."""

    working_directory: Path
    docx_files: tuple[Path, ...]
    pdf_files: tuple[Path, ...]
    archive_file: Path | None
    notes: tuple[str, ...]


def _docx_paths_from_generated(generated: GeneratedDocumentPaths) -> tuple[Path, ...]:
    return (generated.contract_path, generated.completion_certificate_path)


def _build_archive_stem(payload: DocumentIntakePayload) -> str:
    return safe_filename(
        (
            f"document-bundle-"
            f"{payload.contract_number}-"
            f"{payload.certificate_number}-"
            f"{payload.contract_date}"
        )
    )


async def prepare_export_bundle(
    payload: DocumentIntakePayload,
    settings: AppSettings,
) -> ExportBundle:
    """Prepare DOCX files and optional PDF/ZIP exports in isolated workspace."""
    working_directory = await create_temporary_working_directory(
        base_dir=settings.storage.output_dir,
        prefix=settings.storage.working_dir_prefix,
    )
    logger.info("Created temporary working directory=%s", working_directory)

    try:
        generated = await asyncio.to_thread(
            generate_documents,
            payload,
            settings.storage.templates_dir,
            working_directory,
            settings.documents.default_city,
        )
    except (DocumentGenerationError, FileNotFoundError) as exc:
        logger.exception("DOCX generation failed for payload document_type=%s", payload.document_type)
        await remove_path(working_directory)
        raise ExportPreparationError("DOCX generation failed.") from exc

    docx_files = _docx_paths_from_generated(generated)
    pdf_files: tuple[Path, ...] = tuple()
    notes: list[str] = []

    if settings.features.enable_pdf_conversion:
        conversion_results = await convert_documents_to_pdf(
            docx_files=docx_files,
            output_dir=working_directory,
            preferred_backend=settings.features.pdf_backend,
        )
        pdf_files = tuple(result.output_pdf for result in conversion_results if result.output_pdf is not None)
        failed = [result for result in conversion_results if not result.success]
        if failed:
            notes.append(
                "PDF conversion was not available for all files. DOCX output is still ready."
            )

    archive_file: Path | None = None
    if settings.features.enable_zip_export:
        archive_sources = docx_files + pdf_files
        try:
            archive_result = await create_archive(
                files=archive_sources,
                output_dir=working_directory,
                archive_stem=_build_archive_stem(payload),
            )
            archive_file = archive_result.archive_path
            logger.info(
                "ZIP archive prepared path=%s files=%d",
                archive_result.archive_path,
                archive_result.files_included,
            )
        except Exception:
            logger.exception("ZIP archive generation failed.")
            notes.append("ZIP archive generation failed. Individual files are still available.")

    return ExportBundle(
        working_directory=working_directory,
        docx_files=docx_files,
        pdf_files=pdf_files,
        archive_file=archive_file,
        notes=tuple(notes),
    )
