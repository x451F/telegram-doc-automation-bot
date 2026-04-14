"""ZIP archive generation for document export bundles."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from app.services.text_utils import safe_filename


logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class ArchiveOutput:
    """Result metadata for generated ZIP archive."""

    archive_path: Path
    files_included: int


def build_archive_filename(stem: str) -> str:
    """Build deterministic and filesystem-safe archive filename."""
    return f"{safe_filename(stem)}.zip"


def _create_archive_sync(files: tuple[Path, ...], archive_path: Path) -> ArchiveOutput:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive_path, mode="w", compression=ZIP_DEFLATED) as archive:
        for source in files:
            archive.write(source, arcname=source.name)
    return ArchiveOutput(archive_path=archive_path, files_included=len(files))


async def create_archive(
    files: tuple[Path, ...],
    output_dir: Path,
    archive_stem: str,
) -> ArchiveOutput:
    """Create ZIP archive from provided files in a thread off the event loop."""
    archive_name = build_archive_filename(archive_stem)
    archive_path = output_dir / archive_name
    result = await asyncio.to_thread(_create_archive_sync, files, archive_path)
    logger.info("Created ZIP archive path=%s files=%d", result.archive_path, result.files_included)
    return result
