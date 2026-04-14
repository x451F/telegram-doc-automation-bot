from app.services.text_utils import join_non_empty, safe_filename


def test_safe_filename_normalizes_and_truncates() -> None:
    assert safe_filename("  Contract № 42 / Draft  ") == "contract-no-42-draft"
    assert safe_filename("A" * 120, max_length=10) == "aaaaaaaaaa"


def test_join_non_empty_skips_blank_items() -> None:
    items = [" first ", "", "   ", "second"]
    assert join_non_empty(items) == "first, second"

