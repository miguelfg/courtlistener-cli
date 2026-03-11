# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
make install        # runtime deps via uv sync
make install-dev    # editable install with dev extras

# Development
make lint           # ruff check + format (with --fix)
make format         # ruff formatter only
make test           # pytest -v --tb=short
make run            # display CLI help

# Run a single test
python3 -m pytest tests/test_cli.py::test_function_name -v

# Run the CLI
courtlistener-cli --help
```

## Architecture

The CLI is built with Click and structured as:

```
src/
  cli.py              # Main entry point; registers all command groups
  client.py           # CourtListenerClient — httpx wrapper with Bearer auth
  config.py           # Singleton Config; loads .env via python-dotenv
  pagination.py       # paginate_endpoint() — core pagination logic
  output.py           # save_json/csv/xlsx + flatten_dict for tabular export
  batch_processor.py  # read_csv/json_lines/xlsx_batch for bulk input
  commands/           # One file per resource (opinions, search, dockets, etc.)
```

**Command groups:** `opinions`, `search`, `dockets`, `courts`, `people`, `audio`, `batch`

Each command group follows this pattern:
1. Parse Click options
2. Instantiate `CourtListenerClient`
3. Call `paginate_endpoint()` or a direct API call
4. Export via `save_json/csv/xlsx()`

### Pagination semantics (`src/pagination.py`)

`paginate_endpoint(fetch_page, limit, max_pages, ...)`:
- `limit > 0` — stop after N total rows
- `limit == 0, max_pages > 0` — no row cap, stop at page N
- `limit == 0, max_pages == 0` — fetch until API has no `next`

Returns: `{"count", "returned_count", "pages_fetched", "results"}`

### Output (`src/output.py`)

`flatten_dict()` converts nested dicts to dot-notation keys for CSV/XLSX. Timestamp inclusion controlled by `INCLUDE_TIMESTAMP` env var.

### Batch queries (`src/commands/dockets_commands.py`)

Reads a column from CSV/XLSX, loops through values, makes paginated queries per value, and appends `_query_value` to each result row.

## Environment Variables

Copy `.env.example` to `.env`:

| Variable | Default | Purpose |
|---|---|---|
| `COURTLISTENER_API_TOKEN` | — | Required; Bearer token |
| `COURTLISTENER_BASE_URL` | `https://www.courtlistener.com/api/rest/v4` | API base URL |
| `COURTLISTENER_TIMEOUT` | `30` | Request timeout (seconds) |
| `LOG_LEVEL` | `DEBUG` | Logging verbosity |
| `LOG_TO_FILE` | `false` | Write logs to file |
| `OUTPUT_FORMAT` | `xlsx` | Default output format |
| `INCLUDE_TIMESTAMP` | `true` | Timestamp in output filenames |

## Testing

Tests use pytest + Click's `CliRunner` + `monkeypatch` to mock HTTP calls. Test files: `tests/test_cli.py`, `tests/test_client.py`.

When adding a new command, follow the parametrized count-command pattern in `test_cli.py` and add a fixture that patches `CourtListenerClient.get`.

## Search Types

The `search query` command supports `--type d|r|rd`:
- `d` — dockets only
- `r` — dockets + up to 3 matching filings
- `rd` — filing documents only

See `docs/SEARCH_TYPES.md` for details.
