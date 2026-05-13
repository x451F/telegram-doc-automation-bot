# telegram-docx-workflow-bot

Production-style Telegram bot built with **Python 3.11**, **aiogram 3**, and
DOCX templates. The bot collects structured document data through a multi-step
chat workflow, validates and normalizes the input, renders DOCX files, and can
optionally convert them to PDF and package all generated artifacts into a ZIP
archive.

The project is meant to be a practical reference for Telegram-based document
automation without introducing a large web stack.

## What It Does

- Runs an FSM-based intake workflow for service agreements and completion
  certificates.
- Collects contract details, dates, work items, monetary amounts, and certificate
  details step by step.
- Validates and normalizes user input before document generation.
- Renders `.docx` templates with neutral placeholders.
- Generates two output documents per completed workflow:
  - service agreement;
  - completion certificate.
- Converts DOCX files to PDF when enabled and when a backend is available.
- Creates an optional ZIP archive containing the generated files.
- Uses isolated temporary directories for each generation flow.
- Cleans temporary files after Telegram delivery when configured.

## Architecture & Reliability

The bot is structured around a document workflow rather than a single command
handler. Telegram handlers are responsible for interaction and FSM transitions;
document processing lives in services.

```text
Telegram user
  -> aiogram handlers
  -> FSM state storage
  -> validation / normalization
  -> typed payload
  -> template placeholder mapping
  -> DOCX generation
  -> optional PDF conversion
  -> optional ZIP packaging
  -> Telegram file delivery
```

Key reliability choices:

- FSM state management keeps multi-step user input explicit and recoverable.
- Back and cancel navigation are handled separately from business logic.
- Validation happens before payload construction and document rendering.
- PDF conversion is optional and uses fallback order:
  `docx2pdf` -> `soffice`, unless a preferred backend is configured.
- PDF failures do not block DOCX delivery.
- ZIP failures do not block individual file delivery.
- Each export runs in a temporary workspace under `OUTPUT_DIR`.
- Cleanup is controlled by `CLEANUP_TEMP_FILES`.
- Configuration is environment-based and loaded from `.env`.

## Project Structure

```text
app/
  bot.py                    # aiogram bootstrap and long polling entrypoint
  config.py                 # environment-based settings
  states.py                 # FSM state definitions
  handlers/                 # Telegram commands, callbacks, messages, navigation
  keyboards/                # reusable inline/reply keyboard builders
  services/                 # validation, rendering, PDF, ZIP, file lifecycle
  data/                     # workflow catalog data
  templates/                # DOCX templates used at runtime
docs/
  architecture.md           # architecture notes
  portfolio_notes.md        # project positioning notes
  templates/                # readable Markdown drafts of templates
tests/                      # focused unit tests
.github/workflows/          # CI lint workflow
```

## Requirements

- Python 3.11+
- Telegram bot token from BotFather
- Optional: LibreOffice available as `soffice` on `PATH` for PDF fallback

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env` and set:

```env
BOT_TOKEN=replace-with-your-bot-token
```

Run the bot:

```bash
python -m app.bot
```

You can also install from `requirements.txt` for a simpler runtime setup:

```bash
pip install -r requirements.txt
```

## Configuration

| Variable | Default | Description |
|---|---:|---|
| `BOT_TOKEN` | required | Telegram bot token. |
| `PARSE_MODE` | `HTML` | Default Telegram parse mode. |
| `LOG_LEVEL` | `INFO` | Python logging level. |
| `OUTPUT_DIR` | `./output` | Base directory for generated artifacts. |
| `TEMPLATES_DIR` | `./app/templates` | Directory containing runtime `.docx` templates. |
| `DATA_DIR` | `./app/data` | Directory for workflow data files. |
| `WORK_ITEMS_FILE` | `./app/data/work_items.example.json` | Work item catalog used by inline selection. |
| `ENABLE_PDF_CONVERSION` | `false` | Enables DOCX to PDF conversion. |
| `PDF_BACKEND` | `auto` | `auto`, `docx2pdf`, or `soffice`. |
| `ENABLE_ZIP_EXPORT` | `true` | Enables ZIP bundle generation. |
| `CLEANUP_TEMP_FILES` | `true` | Removes temporary export directories after delivery. |
| `ALLOWED_TEMPLATE_EXTENSIONS` | `.docx` | Allowed template file extensions. |
| `DEFAULT_CITY` | `Sample City` | City value injected into templates. |
| `WORKING_DIR_PREFIX` | `job` | Prefix for temporary generation folders. |
| `ADMIN_ALLOWLIST` | empty | Comma-separated Telegram user IDs. Empty means all users are allowed. |

## User Workflow

1. User starts with `/new` or the main menu.
2. Bot asks for the document type.
3. User enters or selects contract number and contract date.
4. User chooses how many work items to include.
5. User selects catalog work items or enters custom text.
6. User enters contract total amount and net amount.
7. User enters certificate number and certificate date.
8. Bot automatically generates the amount in words.
9. User reviews the collected payload.
10. User submits, goes back to edit, or cancels.
11. Bot sends generated DOCX files, optional PDFs, and optional ZIP archive.

## Templates

Runtime templates live in:

- `app/templates/contract_template.docx`
- `app/templates/completion_certificate_template.docx`

Readable source drafts live in:

- `docs/templates/contract_template.md`
- `docs/templates/completion_certificate_template.md`

Supported placeholders include:

| Placeholder | Description |
|---|---|
| `[contract_number]` | Service agreement number. |
| `[contract_date]` | Service agreement date. |
| `[city]` | City from `DEFAULT_CITY`. |
| `[contract_total_amount]` | Contract total amount. |
| `[net_amount]` | Net amount. |
| `[certificate_number]` | Completion certificate number. |
| `[certificate_date]` | Completion certificate date. |
| `[certificate_amount]` | Certificate amount. |
| `[certificate_amount_text]` | Amount in words. |
| `[contractor_name]` | Default contractor name. |
| `[contractor_details]` | Default contractor details. |
| `[client_name]` | Default client name. |
| `[client_representative]` | Default client representative. |
| `[client_details]` | Default client details. |
| `[client_basis]` | Default client basis text. |
| `[additional_notes]` | Reserved optional notes field. |
| `[contract_work_1]` ... `[contract_work_5]` | Agreement work item slots. |
| `[certificate_work_1]` ... `[certificate_work_5]` | Certificate work item slots. |

If more than five work items are collected, the mapping layer preserves the
first four slots and collapses the remaining items into the fifth slot.

## PDF and ZIP Behavior

PDF conversion is controlled by:

```env
ENABLE_PDF_CONVERSION=true
PDF_BACKEND=auto
```

Supported PDF backends:

- `docx2pdf`, available through the optional Python dependency;
- `soffice`, available through LibreOffice.

When `PDF_BACKEND=auto`, the bot tries `docx2pdf` first and then `soffice`.
If conversion fails, the bot still delivers DOCX files and reports a note to the
user.

ZIP export is controlled by:

```env
ENABLE_ZIP_EXPORT=true
```

If ZIP generation fails, individual DOCX and PDF files are still delivered.

## Development

Run tests:

```bash
pytest
```

Run lint and formatting checks:

```bash
ruff check .
ruff format --check .
```

Install optional PDF support:

```bash
pip install -e ".[pdf]"
```

CI runs Ruff checks on pushes and pull requests to `main`.

## Troubleshooting

**Bot fails on startup**

Check that `BOT_TOKEN` is set in `.env` or the process environment.

**PDF files are not generated**

Enable `ENABLE_PDF_CONVERSION=true` and install either `docx2pdf` or
LibreOffice. DOCX output should still be generated without PDF support.

**ZIP archive is missing**

Check `ENABLE_ZIP_EXPORT=true` and verify that `OUTPUT_DIR` is writable.

**Template rendering fails**

Verify that both runtime DOCX templates exist in `app/templates` and that the
placeholder names match the supported placeholder list.

**User is denied access**

If `ADMIN_ALLOWLIST` is set, make sure it contains the numeric Telegram user ID.

## Documentation

- [Architecture notes](docs/architecture.md)
- [Portfolio notes](docs/portfolio_notes.md)
- [Contributing guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## License

MIT. See [LICENSE](LICENSE).
