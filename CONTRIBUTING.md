# Contributing

Thanks for your interest in improving `telegram-docx-workflow-bot`.

## Ground Rules

- Keep all code and user-visible text in English.
- Keep the project generic and reusable; avoid domain-specific or private data.
- Keep export and generation logic inside services, not handlers.
- Add or update tests for any pure utility logic you change.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

## Quality Checks

Run these checks before opening a pull request:

```bash
ruff check .
ruff format --check .
pytest
```

## Pull Request Checklist

1. Keep changes focused and documented.
2. Update `README.md` and `CHANGELOG.md` when behavior changes.
3. Ensure linting passes.
4. Ensure no private strings, personal data, or internal identifiers are introduced.

