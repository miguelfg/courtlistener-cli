# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make install       # sync runtime dependencies
make install-dev   # editable install with dev extras (uv)
make test          # pytest -v --tb=short
make lint          # ruff check + format check
make format        # ruff formatter only
make run           # courtlistener-cli --help
make opinions-list # quick opinions query example
```

Run a single test:
```bash
uv run pytest tests/test_cli.py::test_opinions_list_shows_token_hint_on_auth_error -v
```

## Architecture

Python CLI (Click) wrapping the CourtListener REST API.

**Entry point:** `src/cli.py` — registers 7 Click groups: `opinions`, `search`, `courts`, `dockets`, `people`, `audio`, `batch`.

**Core modules:**
- `src/client.py` — `CourtListenerClient` using httpx with Bearer auth. Single class, methods: `get/post/put/delete`.
- `src/pagination.py` — `paginate_endpoint()` drives all list commands. Three modes: `limit > 0` (stop at N records), `limit == 0, max_pages > 0` (page cap only), `limit == 0, max_pages == 0` (unbounded).
- `src/output.py` — exports to JSON/CSV/XLSX; flattens nested structures for tabular formats.
- `src/config.py` — singleton loading `.env` via python-dotenv. Key vars: `COURTLISTENER_API_TOKEN`, `BASE_URL`, `TIMEOUT`, `LOG_LEVEL`, `OUTPUT_FORMAT`.
- `src/batch_processor.py` — handles CSV/JSON Lines batch input files.

**Command modules** (`src/commands/`): one module per resource type, each with Click group + subcommands (`list`, `get`, batch ops). All list commands use `paginate_endpoint()` and share `--limit`, `--max-pages`, `--format`, `--output` options.

**Tests** use `pytest` + Click's `CliRunner` for integration-style CLI testing. Mock the client for error path coverage.

## Coding Style

- Python 3.8+; 4-space indentation; PEP 8.
- `snake_case` for modules/functions/variables; `PascalCase` for classes.
- Keep CLI command names and options consistent with existing Click patterns.
- Prefer small, focused handlers under `src/commands/`.

## Testing

- Use Click's `CliRunner`; name functions `test_<behavior>()`.
- Cover success and failure paths (auth errors, required args, batch input edge cases).

## Conventions

- Add new resources as a new file in `src/commands/`, register the group in `src/cli.py`.
- Run `make lint` before opening a PR.
- Commit style: conventional prefix (`feat(scope):`, `fix(scope):`, `docs(scope):`); one logical change per commit.
- PRs should state what changed and why, key commands run (`make test`, `make lint`), and a sample CLI invocation when behavior changes.
- Secrets via `.env` only — never commit `COURTLISTENER_API_TOKEN`.
- `LOG_LEVEL=DEBUG` for troubleshooting.
