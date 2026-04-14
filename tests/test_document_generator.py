from pathlib import Path

from app.services.document_generator import build_output_filename, resolve_template_files


def test_build_output_filename_is_deterministic_and_safe() -> None:
    result = build_output_filename(
        prefix="service-agreement",
        number="AGR/2026 №1",
        date_value="2026-04-14",
    )
    assert result == "service-agreement-agr-2026-no1-2026-04-14.docx"


def test_resolve_template_files_paths() -> None:
    templates = resolve_template_files(Path("/tmp/templates"))
    assert templates.contract_template_path == Path("/tmp/templates/contract_template.docx")
    assert templates.completion_certificate_template_path == Path(
        "/tmp/templates/completion_certificate_template.docx"
    )

