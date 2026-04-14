import asyncio
from pathlib import Path

from app.services.file_service import create_temporary_working_directory, remove_path


def test_temporary_working_directory_create_and_cleanup(tmp_path: Path) -> None:
    work_dir = asyncio.run(create_temporary_working_directory(tmp_path, prefix="unit"))
    assert work_dir.exists()
    assert work_dir.is_dir()

    sample_file = work_dir / "sample.txt"
    sample_file.write_text("payload", encoding="utf-8")
    assert sample_file.exists()

    asyncio.run(remove_path(work_dir))
    assert not work_dir.exists()

