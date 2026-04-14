# telegram-docx-workflow-bot

Telegram bot project built with Python and aiogram 3 for reusable document workflows based on DOCX templates.

## Public Repository Intent

This repository is designed as a generalized document automation bot that can be reused across different teams and domains. It focuses on configurable placeholders, multi-step data collection, and export-friendly outputs rather than any domain-specific business process.

## Migration Note

This public version is a generalized rewrite of a private internal prototype. Sensitive implementation details were intentionally removed and replaced with neutral, reusable abstractions.

## Features (Current Milestone)

- aiogram 3 bot bootstrap with modular structure
- FSM state definitions for multi-step document workflows
- Utility services for date and text normalization
- Environment-based configuration (`.env`)
- Optional feature flags for PDF conversion and ZIP export

## Planned Workflow

1. User starts a conversation in Telegram.
2. Bot collects fields in a multi-step FSM flow (`contract_number`, `contract_date`, `certificate_number`, `work_items`).
3. Service layer renders DOCX output from selected templates.
4. Optional conversion/export pipeline creates PDF and ZIP artifacts.

## Project Structure

```text
app/
  bot.py
  config.py
  states.py
  handlers/
  keyboards/
  services/
  data/
  templates/
docs/
tests/
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
python -m app.bot
```

## Development

```bash
python -m pytest
python -m ruff check .
python -m mypy app
```

## License

MIT

