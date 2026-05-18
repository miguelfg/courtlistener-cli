# [PROJECT_NAME]

<!-- fill: PRD title + one-line description from PRD Introduction > Overview -->
[DESCRIPTION]

**Base URL:** `[BASE_URL]`
<!-- fill: PRD **Base URL:** field -->

---

## Installation

```bash
uv sync
```

> Or with pip: `pip install -r requirements.txt`

## Configuration

```bash
cp .env.example .env
```

<!-- fill: read .env.example, list only the required variables (no defaults) -->
Required environment variables:

```env
[REQUIRED_ENV_VARS]
```

Full options: see `.env.example`.

---

## Help

<!-- fill: run `uv run [CLI_NAME] --help` and paste output verbatim -->
```
[CLI_HELP_OUTPUT]
```

### Resource commands

<!-- fill: for each resource group, run `uv run [CLI_NAME] [resource] --help` and paste output -->
[RESOURCE_HELP_SECTIONS]

---

## Batch Processing

<!-- fill: copy the module docstring from src/batch_processor.py (the supported commands table) -->
Input file format — `data/batch.txt`, one JSON object per line:

```jsonl
[BATCH_DOCSTRING_EXAMPLES]
```

```bash
[CLI_NAME] batch --input-file data/batch.txt --output-dir output/
```

Output: `output/batch_results_[TIMESTAMP_FORMAT].xlsx` — sheets: Summary, Results, Errors.

---

## Development

<!-- fill: run `make help` (or `uv run make help`) in the project root and paste output -->
```
[MAKE_HELP_OUTPUT]
```

---

## Project Structure

<!-- fill: run `tree -a -I '__pycache__|*.pyc|uv.lock|.env|output|logs|.pytest_cache' --dirsfirst` -->
```
[TREE_OUTPUT]
```

---

## API Reference

**Authentication:** `[AUTH_HEADER]` header
<!-- fill: auth header name from PRD Authentication section -->

Full endpoint reference: [`[PRD_FILENAME]`]([PRD_PATH])
<!-- fill: relative path from project root to the source PRD.md -->
