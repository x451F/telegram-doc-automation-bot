# telegram-docx-workflow-bot

Telegram bot project built with Python and aiogram 3 for reusable document workflows based on DOCX templates.

## Project Background

This repository is a public-safe generalized rewrite of a private client project that I originally developed for document workflow automation.

The original implementation included client-specific business rules, personalized templates, and private operational details. This public version was redesigned to preserve the reusable technical architecture while removing all sensitive and domain-specific content.

## Public Repository Intent

This repository is designed as a reusable document automation bot that can be adapted across different teams and domains. It focuses on configurable placeholders, multi-step data collection, template-driven document generation, and export-friendly outputs rather than any client-specific business process.

## Migration Note

This public version is a generalized rewrite of a private internal prototype. Sensitive implementation details were intentionally removed and replaced with neutral, reusable abstractions.

## Features (Current Milestone)

- aiogram 3 FSM intake flow for document payload collection
- Dynamic work item catalog loaded from JSON configuration
- Inline presets for document numbers, dates, counts, and amounts
- Back/cancel navigation across conversation steps
- Optional admin allowlist via environment configuration
- Utility services for date/text normalization and validation
- Optional PDF export with backend fallback (`docx2pdf` -> `soffice`)
- ZIP archive export for generated artifacts
- Safe temporary working directories with optional cleanup
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

## PDF support notes

- PDF conversion is optional and controlled by `ENABLE_PDF_CONVERSION`.
- Backend order is configurable via `PDF_BACKEND`:
1. `auto` (default): try `docx2pdf`, then fallback to LibreOffice `soffice`
2. `docx2pdf`: prefer `docx2pdf`, then fallback to `soffice`
3. `soffice`: prefer `soffice`, then fallback to `docx2pdf`
- If neither backend is available, the bot still returns DOCX files and logs the reason.

## ZIP export notes

- ZIP export is controlled by `ENABLE_ZIP_EXPORT`.
- The archive includes all generated files available for the run:
1. DOCX files (always)
2. PDF files (when conversion succeeds)
- ZIP generation errors do not crash the bot; individual files are still sent.

## Environment variable examples

```env
BOT_TOKEN=replace-with-your-bot-token
OUTPUT_DIR=./output
TEMPLATES_DIR=./app/templates
WORKING_DIR_PREFIX=job

ENABLE_PDF_CONVERSION=true
PDF_BACKEND=auto
ENABLE_ZIP_EXPORT=true
CLEANUP_TEMP_FILES=true

DEFAULT_CITY=Sample City
ADMIN_ALLOWLIST=123456789,987654321
```

## Templates and placeholders

Template files are stored in `app/templates`:

- `contract_template.docx`
- `completion_certificate_template.docx`

Readable template drafts are stored in `docs/templates`:

- `contract_template.md`
- `completion_certificate_template.md`

The generator replaces placeholders in both paragraphs and table cells.
Output `.docx` files are written to the configured `OUTPUT_DIR` (default: `./output`) with deterministic filenames.

### Placeholder reference

| Placeholder | Description |
|---|---|
| `[contract_number]` | Service agreement number |
| `[contract_date]` | Service agreement date |
| `[city]` | City label from configuration (`DEFAULT_CITY`) |
| `[contract_total_amount]` | Contract total amount |
| `[net_amount]` | Net amount |
| `[certificate_number]` | Completion certificate number |
| `[certificate_date]` | Completion certificate date |
| `[certificate_amount]` | Certificate amount value |
| `[certificate_amount_text]` | Certificate amount in words |
| `[contract_work_1]` ... `[contract_work_5]` | Agreement work item lines |
| `[certificate_work_1]` ... `[certificate_work_5]` | Certificate work item lines |

## Troubleshooting

1. PDF files are not generated:
Ensure `ENABLE_PDF_CONVERSION=true` and install at least one backend:
- `pip install -e ".[pdf]"`
- or install LibreOffice and ensure `soffice` is on `PATH`.
2. Bot sends DOCX but no ZIP:
Check `ENABLE_ZIP_EXPORT=true` and verify write access to `OUTPUT_DIR`.
3. Template rendering fails:
Confirm both template files exist in `app/templates`:
- `contract_template.docx`
- `completion_certificate_template.docx`
4. Access denied for valid user:
If `ADMIN_ALLOWLIST` is set, verify the Telegram numeric user ID is included.

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
