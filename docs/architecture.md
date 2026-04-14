# Architecture Notes

## Overview

`telegram-docx-workflow-bot` follows a layered structure:

- `handlers`: Telegram update entrypoints and FSM transitions.
- `keyboards`: reusable UI builders and callback schemas.
- `services`: document generation, validation, conversion, archive, and file lifecycle.
- `templates`: DOCX templates with neutral placeholders.
- `data`: configurable workflow catalogs (for example work item options).

## Runtime Flow

1. User progresses through FSM steps to provide structured document fields.
2. Payload is validated and mapped to placeholders.
3. DOCX files are generated from templates.
4. Optional PDF conversion runs with backend fallback.
5. Optional ZIP archive is generated from all available outputs.
6. Files are sent back through Telegram.
7. Temporary workspace is cleaned up when enabled.

## Reliability Principles

- Degrade gracefully when PDF backends are unavailable.
- Keep filesystem operations off the event loop with `asyncio.to_thread`.
- Keep export logic in service layer, not in Telegram handlers.
- Use module-level logging for operator visibility and debugging.
