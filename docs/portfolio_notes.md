# Portfolio Notes

## What Problems This Project Solves

`telegram-docx-workflow-bot` demonstrates a reusable pattern for teams that need:

- structured document intake over chat,
- template-driven DOCX generation,
- optional export formats (PDF, ZIP),
- and a maintainable service-oriented bot architecture.

It provides a clean reference implementation for production-minded Telegram automation without domain-specific coupling.

## Engineering Decisions

### 1. Layered architecture

- `handlers` orchestrate user interaction and state transitions.
- `services` own business logic, generation, conversion, and file lifecycle.
- `keyboards` isolate UI construction from behavior.

This keeps interaction logic thin and makes service code easier to test and extend.

### 2. FSM-first workflow

The intake flow is built on aiogram FSM states to enforce deterministic step ordering and explicit validation at each step.

### 3. Template mapping abstraction

Collected payload data is transformed into placeholder dictionaries before rendering. This decouples conversational schema from template implementation details.

### 4. Export resilience

PDF conversion is optional and backend-agnostic:

- tries `docx2pdf` when installed,
- falls back to `soffice` when available,
- degrades gracefully to DOCX-only output when neither is present.

ZIP export and temporary workspace cleanup are isolated in dedicated services.

## Trade-offs Considered

- **Direct formatting preservation vs simple replacement:**  
  Paragraph-level replacement is intentionally simple and robust, but can reset rich run-level formatting in edge cases.

- **Strict backend dependency vs graceful optional behavior:**  
  PDF conversion is not mandatory to avoid platform lock-in and to keep local setup lightweight.

- **Monolithic handler logic vs service orchestration:**  
  More modules introduce extra files, but improve readability and long-term maintainability.

