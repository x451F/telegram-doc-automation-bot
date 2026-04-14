# telegram-docx-workflow-bot

Production-style Telegram bot example built with **Python + aiogram 3** for structured document intake and template-based file generation.

This repository is designed as a reusable reference for:

- FSM-driven chat workflows,
- DOCX template rendering with placeholders,
- optional PDF conversion with graceful backend fallback,
- ZIP export and safe temporary file lifecycle.

## Why This Project

Many teams need lightweight automation for service documents but do not need a large web stack.  
This project demonstrates a clean architecture for collecting structured data in Telegram and producing export-ready files in a maintainable way.

## Feature Highlights

- Multi-step FSM intake flow with validation and back/cancel navigation
- Generic payload fields (`contract_number`, `contract_date`, `work_items`, etc.)
- DOCX generation from neutral placeholders in paragraphs and table cells
- Optional PDF conversion (`docx2pdf` then `soffice` fallback)
- Optional ZIP bundle generation
- Safe per-request temporary workspace + optional cleanup
- Config-driven behavior via environment variables
- Lint-ready and CI-ready project structure

## Architecture Overview

High-level modules:

- `app/handlers`: user interaction and FSM transitions only
- `app/keyboards`: reusable Telegram keyboard builders
- `app/services`: validation, mapping, rendering, conversion, archiving, file lifecycle
- `app/templates`: demo DOCX templates
- `app/data`: configurable workflow catalogs
- `docs`: architecture and portfolio notes
- `tests`: utility-focused test coverage

The core principle is strict separation between interaction and processing logic.

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
  architecture.md
  portfolio_notes.md
tests/
.github/workflows/
```

## Setup

### Requirements

- Python 3.11+
- Telegram bot token
- Optional for PDF fallback: LibreOffice (`soffice`) on `PATH`

### Local Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

### Run

```bash
python -m app.bot
```

## Example Workflow

1. Start with `/new` or **Start Intake Workflow**
2. Choose document type
3. Enter contract number/date
4. Select work item count and items
5. Enter amounts
6. Enter certificate number/date
7. Enter amount in words
8. Submit payload
9. Receive generated DOCX files
10. Receive PDF files when conversion backend is available
11. Receive ZIP archive when enabled

## Templates and Placeholders

Template files:

- `app/templates/contract_template.docx`
- `app/templates/completion_certificate_template.docx`

Readable source drafts:

- `docs/templates/contract_template.md`
- `docs/templates/completion_certificate_template.md`

### Placeholder Reference

| Placeholder | Description |
|---|---|
| `[contract_number]` | Service agreement number |
| `[contract_date]` | Service agreement date |
| `[city]` | City value from config (`DEFAULT_CITY`) |
| `[contract_total_amount]` | Contract total amount |
| `[net_amount]` | Net amount |
| `[certificate_number]` | Completion certificate number |
| `[certificate_date]` | Completion certificate date |
| `[certificate_amount]` | Certificate amount |
| `[certificate_amount_text]` | Certificate amount in words |
| `[contract_work_1]` ... `[contract_work_5]` | Agreement work item slots |
| `[certificate_work_1]` ... `[certificate_work_5]` | Certificate work item slots |

## PDF and ZIP Notes

- PDF conversion is optional (`ENABLE_PDF_CONVERSION=true`)
- Backend strategy is configurable (`PDF_BACKEND=auto|docx2pdf|soffice`)
- If no PDF backend is available, the bot still returns DOCX files
- ZIP export is optional (`ENABLE_ZIP_EXPORT=true`)
- ZIP errors do not break DOCX/PDF delivery

## Environment Example

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
ADMIN_ALLOWLIST=
```

## Development

```bash
ruff check .
ruff format --check .
pytest
```

CI runs lint checks on pushes and pull requests to `main`.
See also:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)

## Troubleshooting

1. PDF not generated:
Install `docx2pdf` (`pip install -e ".[pdf]"`) or install LibreOffice (`soffice`).
2. ZIP missing:
Check `ENABLE_ZIP_EXPORT` and output directory write permissions.
3. Template errors:
Confirm both DOCX templates exist in `app/templates`.
4. Access denied:
If `ADMIN_ALLOWLIST` is set, verify the Telegram numeric user ID.

## Next Improvements

1. Add async integration tests for the full FSM flow.
2. Support localized template packs and per-chat template selection.
3. Add observability hooks (metrics + structured event IDs).

## License

MIT. See [LICENSE](LICENSE).
