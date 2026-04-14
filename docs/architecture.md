# Architecture Notes

## Overview

`telegram-docx-workflow-bot` follows a layered structure:

- `handlers`: Telegram update entrypoints and FSM transitions.
- `keyboards`: reusable UI builders.
- `services`: pure helper logic and file processing.
- `templates`: document templates consumed by render services.
- `data`: runtime metadata and generated artifacts.

## Milestone Scope

Current codebase includes startup/bootstrap modules and utility primitives.
Template rendering, PDF conversion, and ZIP packaging are planned as separate services in subsequent milestones.

