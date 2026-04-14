"""Optional DOCX to PDF conversion with graceful backend fallback."""

from __future__ import annotations

import asyncio
import logging
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


logger = logging.getLogger(__name__)


class PDFBackend(str, Enum):
    """Supported PDF conversion backends."""

    DOCX2PDF = "docx2pdf"
    SOFFICE = "soffice"


@dataclass(slots=True, frozen=True)
class PDFConversionResult:
    """Per-file conversion outcome."""

    source_docx: Path
    output_pdf: Path | None
    backend: str | None
    success: bool
    message: str | None = None


def _resolve_backend_order(preferred_backend: str) -> tuple[PDFBackend, ...]:
    preferred = preferred_backend.strip().lower()
    if preferred == PDFBackend.DOCX2PDF.value:
        return (PDFBackend.DOCX2PDF, PDFBackend.SOFFICE)
    if preferred == PDFBackend.SOFFICE.value:
        return (PDFBackend.SOFFICE, PDFBackend.DOCX2PDF)
    return (PDFBackend.DOCX2PDF, PDFBackend.SOFFICE)


def _convert_with_docx2pdf(source_docx: Path, output_pdf: Path) -> tuple[bool, str | None]:
    try:
        from docx2pdf import convert  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return False, "docx2pdf package is not installed."

    try:
        convert(str(source_docx), str(output_pdf))
    except Exception as exc:  # pragma: no cover - backend dependent
        return False, f"docx2pdf backend failed: {exc}"

    if output_pdf.exists():
        return True, None
    return False, "docx2pdf completed without producing output file."


def _convert_with_soffice(source_docx: Path, output_pdf: Path) -> tuple[bool, str | None]:
    soffice_path = shutil.which("soffice")
    if not soffice_path:
        return False, "LibreOffice soffice executable is not available."

    command = [
        soffice_path,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_pdf.parent),
        str(source_docx),
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        details = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
        return False, f"soffice backend failed: {details}"

    if output_pdf.exists():
        return True, None
    return False, "soffice completed without producing output file."


def _convert_single_sync(
    source_docx: Path,
    output_pdf: Path,
    backend_order: tuple[PDFBackend, ...],
) -> PDFConversionResult:
    errors: list[str] = []
    for backend in backend_order:
        if backend == PDFBackend.DOCX2PDF:
            success, message = _convert_with_docx2pdf(source_docx, output_pdf)
        else:
            success, message = _convert_with_soffice(source_docx, output_pdf)

        if success:
            return PDFConversionResult(
                source_docx=source_docx,
                output_pdf=output_pdf,
                backend=backend.value,
                success=True,
                message=None,
            )
        if message:
            errors.append(message)

    return PDFConversionResult(
        source_docx=source_docx,
        output_pdf=None,
        backend=None,
        success=False,
        message=" | ".join(errors) if errors else "No available PDF backend.",
    )


async def convert_documents_to_pdf(
    docx_files: tuple[Path, ...],
    output_dir: Path,
    preferred_backend: str = "auto",
) -> tuple[PDFConversionResult, ...]:
    """Convert DOCX files to PDF using available backends with fallback."""
    backend_order = _resolve_backend_order(preferred_backend)
    logger.info(
        "PDF conversion requested for %d files with preferred_backend=%s",
        len(docx_files),
        preferred_backend,
    )

    results: list[PDFConversionResult] = []
    for source_docx in docx_files:
        output_pdf = output_dir / f"{source_docx.stem}.pdf"
        result = await asyncio.to_thread(_convert_single_sync, source_docx, output_pdf, backend_order)
        if result.success:
            logger.info(
                "PDF conversion succeeded source=%s backend=%s output=%s",
                source_docx.name,
                result.backend,
                result.output_pdf.name if result.output_pdf else "-",
            )
        else:
            logger.warning(
                "PDF conversion skipped source=%s reason=%s",
                source_docx.name,
                result.message or "unknown",
            )
        results.append(result)

    return tuple(results)

