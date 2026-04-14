"""Work item catalog loading for generic document intake workflows."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class WorkItemOption:
    """Selectable work item option loaded from configuration."""

    code: str
    label: str


def _normalize_option(raw_option: object) -> WorkItemOption | None:
    if not isinstance(raw_option, dict):
        return None

    code = str(raw_option.get("code", "")).strip()
    label = str(raw_option.get("label", "")).strip()
    if not code or not label:
        return None

    return WorkItemOption(code=code, label=label)


def load_work_items_catalog(path: Path) -> tuple[WorkItemOption, ...]:
    """Load work item options from JSON file and return immutable catalog."""
    if not path.exists():
        return tuple()

    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_items = payload.get("work_items", []) if isinstance(payload, dict) else []
    options: list[WorkItemOption] = []
    for raw_item in raw_items:
        option = _normalize_option(raw_item)
        if option is not None:
            options.append(option)
    return tuple(options)

