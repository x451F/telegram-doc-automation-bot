import asyncio
from pathlib import Path
from zipfile import ZipFile

from app.services.archive_service import build_archive_filename, create_archive


def test_build_archive_filename_is_safe() -> None:
    assert build_archive_filename("Bundle 2026/04") == "bundle-2026-04.zip"


def test_create_archive_creates_zip(tmp_path: Path) -> None:
    first = tmp_path / "a.txt"
    second = tmp_path / "b.txt"
    first.write_text("alpha", encoding="utf-8")
    second.write_text("beta", encoding="utf-8")

    result = asyncio.run(
        create_archive(
            files=(first, second),
            output_dir=tmp_path,
            archive_stem="bundle-test",
        )
    )

    assert result.archive_path.exists()
    with ZipFile(result.archive_path) as archive:
        names = sorted(archive.namelist())
    assert names == ["a.txt", "b.txt"]

