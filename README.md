# telegram-docx-workflow-bot

Telegram bot project built with Python and aiogram 3 for reusable document workflows based on DOCX templates.

## Public Repository Intent

This repository is designed as a generalized document automation bot that can be reused across different teams and domains. It focuses on configurable placeholders, multi-step data collection, and export-friendly outputs rather than any domain-specific business process.

## Migration Note

This public version is a generalized rewrite of a private internal prototype. Sensitive implementation details were intentionally removed and replaced with neutral, reusable abstractions.

## Features (Current Milestone)

- aiogram 3 FSM intake flow for document payload collection
- Dynamic work item catalog loaded from JSON configuration
- Inline presets for document numbers, dates, counts, and amounts
- Back/cancel navigation across conversation steps
- Optional admin allowlist via environment configuration
- Utility services for date/text normalization and validation
- Environment-based configuration (`.env`)
- Optional feature flags for PDF conversion and ZIP export

## Workflow

1. Start the flow with `/new` or `Start Intake Workflow`.
2. Choose document type: `service_agreement` or `completion_certificate`.
3. Provide `contract_number` and `contract_date`.
4. Provide `work_item_count`, then fill `work_items` from presets or custom input.
5. Provide `contract_total_amount` and `net_amount`.
6. Provide `certificate_number` and `certificate_date`.
7. Provide `amount_in_words`.
8. Review and submit the collected payload.

The workflow is intentionally generic and keeps document generation concerns in the service layer, not in Telegram handlers.

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
