import json
from pathlib import Path

from app.services.work_items import load_work_items_catalog


def test_load_work_items_catalog(tmp_path: Path) -> None:
    payload = {
        "work_items": [
            {"code": "analysis", "label": "Business process analysis"},
            {"code": "support", "label": "Support"},
            {"code": "", "label": "Ignored"},
        ]
    }
    target_file = tmp_path / "items.json"
    target_file.write_text(json.dumps(payload), encoding="utf-8")

    options = load_work_items_catalog(target_file)
    assert len(options) == 2
    assert options[0].code == "analysis"
    assert options[1].label == "Support"

