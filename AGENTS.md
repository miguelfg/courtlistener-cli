# Repository Guidelines

## Project Structure & Module Organization
This repository provides a Python CLI for the CourtListener REST API.

- `src/`: application code.
- `src/cli.py`: Click entrypoint (`courtlistener-cli`).
- `src/commands/`: command groups (`opinions`, `dockets`, `search`, etc.).
- `src/client.py`: HTTP client and auth/header behavior.
- `tests/`: pytest suite (`test_cli.py`, `test_client.py`).
- `data/`: sample inputs for batch flows.
- `docs/`: API schema and project notes.
- `output/`: generated exports (JSON/CSV/XLSX).

## Build, Test, and Development Commands
Use `uv` and the Makefile wrappers:

- `make install`: sync runtime dependencies.
- `make install-dev`: install editable package with dev extras.
- `make run`: show CLI help (`uv run courtlistener-cli --help`).
- `make opinions-list`: run a quick opinions query example.
- `make test`: run `pytest` with verbose short tracebacks.
- `make lint`: run Ruff checks and formatting.
- `make format`: run Ruff formatter only.

## Coding Style & Naming Conventions
- Python 3.8+; 4-space indentation; keep code PEP 8-compliant.
- Prefer small, focused command handlers under `src/commands/`.
- Use `snake_case` for modules/functions/variables; `PascalCase` for classes.
- Keep CLI command names and options consistent with existing Click patterns.
- Run `make lint` before opening a PR.

## Testing Guidelines
- Framework: `pytest` with Click’s `CliRunner` for CLI behavior.
- Add tests in `tests/test_*.py`; name test functions `test_<behavior>()`.
- Cover success and failure paths (auth errors, required args, batch input edge cases).
- Run locally with `make test`.

## Commit & Pull Request Guidelines
- Follow concise, imperative commit subjects.
- Preferred pattern (seen in history): conventional prefix like `feat(docs): ...`; otherwise short action-style messages (`Fix ...`, `Add ...`).
- Keep each commit scoped to one logical change.
- PRs should include:
  - what changed and why,
  - key commands run (`make test`, `make lint`),
  - sample CLI invocation/output when behavior changes.

## Security & Configuration Tips
- Configure secrets via `.env` (see `.env.example`); do not commit API tokens.
- Primary variable: `COURTLISTENER_API_TOKEN`.
- For troubleshooting, set `LOG_LEVEL=DEBUG`.
