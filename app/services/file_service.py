"""Safe temporary workspace helpers for generated document artifacts."""

from __future__ import annotations

import asyncio
import logging
import shutil
import tempfile
from pathlib import Path


logger = logging.getLogger(__name__)


async def ensure_directory(path: Path) -> Path:
    """Ensure directory exists using a thread-safe filesystem operation."""
    await asyncio.to_thread(path.mkdir, parents=True, exist_ok=True)
    return path


async def create_temporary_working_directory(base_dir: Path, prefix: str = "job") -> Path:
    """Create isolated temporary workspace inside configured output directory."""
    await ensure_directory(base_dir)
    created_path = await asyncio.to_thread(
        tempfile.mkdtemp,
        f"{prefix}-",
        "",
        str(base_dir),
    )
    result = Path(created_path)
    logger.info("Temporary working directory created path=%s", result)
    return result


async def remove_path(path: Path) -> None:
    """Remove file or directory recursively if it exists."""
    if not path.exists():
        return
    if path.is_file():
        await asyncio.to_thread(path.unlink, missing_ok=True)
        logger.info("Removed temporary file path=%s", path)
        return
    await asyncio.to_thread(shutil.rmtree, path, True)
    logger.info("Removed temporary directory path=%s", path)
