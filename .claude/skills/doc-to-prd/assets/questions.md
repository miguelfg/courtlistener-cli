# doc-to-prd Interactive Questions

Use these questions during PRD generation. Record answers under `## Implementation Decisions` in `{project_name}_PRD.md`.

Conventions:
- `[single-choice]` means choose exactly one option.
- `[multi-choice]` means choose one or more options.
- `[free-text]` means provide custom text.

## Project Identity

1. CLI name to run with `uv run <cli-name>` [free-text]
   - Example: `stripe-cli`

2. Python version target [single-choice]
   - `>=3.10` (Recommended)
   - `>=3.11`
   - `>=3.12`
   - custom [free-text]

## HTTP Stack

3. HTTP library [single-choice]
   - `requests` (Recommended)
   - `httpx`
   - `aiohttp`
   - `urllib3`

4. Retry/backoff policy [single-choice]
   - Enabled: `3 attempts`, `1s base`, `x2 backoff`, retry on `408,429,500,502,503,504` (Recommended)
   - Disabled
   - custom [free-text]

5. Timeout policy [single-choice]
   - `30s total timeout` (Recommended)
   - `60s total timeout`
   - custom [free-text]

## Authentication

6. Credentials configuration [single-choice]
   - environment variables (Recommended)
   - config file
   - interactively asking

## CLI Behavior

7. Output formats [multi-choice]
   - `json` (Recommended)
   - `csv`
   - `xlsx`
   - `sqlite`

8. Batch mode input formats [single-choice]
   - `csv + txt/jsonl` (Recommended)
   - `csv` only
   - `txt/jsonl` only
   - disabled

9. Output accepted formats and default [single-choice]
   - default `xlsx`; accept `xlsx` only (Recommended)
   - default `xlsx`; accept `xlsx` + `csv`
   - default `xlsx`; accept `xlsx` + `sqlite`
   - default `xlsx`; accept `xlsx` + `csv` + `sqlite`

10. Default save-data mode for repeated identical queries [single-choice]
   - Save in timestamped files (Recommended)
   - Overwrite if target exists
   - Concatenate into the same target and add a request timestamp column

## PRD Recording Template

Use this exact block in generated PRD:

```markdown
## Implementation Decisions

- CLI Name: `<cli-name>`
- Python Version: `<version-policy>`
- HTTP Library: `<requests|httpx|aiohttp|urllib3>`
- Authentication: `<derived from API/OpenAPI source>`
- Credentials Configuration: `<env_vars|config|interactive_prompt>`
- Timeout: `<seconds/policy>`
- Retry Policy: `<summary>`
- Output Formats: `<json,csv,xlsx,sqlite>`
- Output Accepted Formats and Default: `<default_xlsx__accepted_xlsx|default_xlsx__accepted_xlsx_csv|default_xlsx__accepted_xlsx_sqlite|default_xlsx__accepted_xlsx_csv_sqlite>`
- Batch Input Formats: `<csv|txt|both|none>`
- Default Save Data Mode: `<timestamped|overwrite|append_with_request_timestamp>`
- Lint/Format Toolchain: `ruff check --fix` + `ruff format`
```
