# CourtListener Python CLI Client

Python CLI tool for the [CourtListener REST API v4](https://www.courtlistener.com/help/api/rest/). Covers case law, PACER federal court data, judges, oral arguments, financial disclosures, citations, and alerts — with batch processing and XLSX/CSV/JSON export.

## Features

- **18 command groups** — opinions, dockets, clusters, PACER entries/documents, parties, attorneys, people, positions, financial disclosures, oral arguments, search, alerts, citation lookup, tags
- **Cursor-based pagination** — `--limit N` (row cap), `--max-pages N` (page cap), or both at zero for full unbounded crawls
- **Batch processing** — supply a CSV/XLSX file and a column name; the CLI queries once per row and appends `_query_value` to each result
- **Multiple outputs** — JSON, CSV, XLSX; timestamped filenames by default
- **Rate-limit aware** — retries on 429 with `Retry-After`; raises an informative `DailyQuotaExceeded` error when the daily quota is hit
- **Token auth** — `Authorization: Token <token>` header throughout

## Installation

```bash
# Using uv (recommended)
make install        # uv sync
make install-dev    # editable install with dev extras

# Or manually
uv pip install -e .
```

## Quick Start

### 1. Configure API Token

```bash
cp .env.example .env
# Set your token
export COURTLISTENER_API_TOKEN=your_token_here
```

Get your token at [courtlistener.com/profile/api/](https://www.courtlistener.com/profile/api/).

### 2. Verify

```bash
uv run courtlistener-cli --version
uv run courtlistener-cli --help
```

### 3. First queries

```bash
# 10 most recent SCOTUS opinions
uv run courtlistener-cli opinions list --limit 10

# Full-text search for case law
uv run courtlistener-cli search query --q '"gun control"' --type o --limit 25

# List SCOTUS dockets, save as XLSX
uv run courtlistener-cli dockets list --court scotus --limit 50 --format xlsx

# Verify a citation
uv run courtlistener-cli citation-lookup citation --volume 576 --reporter "U.S." --page 644
```

---

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `COURTLISTENER_API_TOKEN` | — | **Required** — Bearer token |
| `COURTLISTENER_BASE_URL` | `https://www.courtlistener.com/api/rest/v4` | API base URL |
| `COURTLISTENER_TIMEOUT` | `30` | Request timeout (seconds) |
| `LOG_LEVEL` | `DEBUG` | Logging verbosity |
| `LOG_TO_FILE` | `false` | Write logs to file |
| `OUTPUT_FORMAT` | `xlsx` | Default output format |
| `INCLUDE_TIMESTAMP` | `true` | Timestamp in output filenames |

### Pagination Behavior (all list commands)

| Flag combination | Behavior |
|---|---|
| `--limit N` | Stop after N rows total across all pages |
| `--max-pages N` | Stop after N pages regardless of row count |
| `--limit 0 --max-pages 10` (default) | No row cap; fetch up to 10 pages |
| `--limit 0 --max-pages 0` | Full unbounded crawl — fetch until API has no `next` |

Progress is printed per page: `→ Page 3: +20 results (accumulated 60/100)`

---

## Available Commands

### opinions

Case law decisions.

```bash
uv run courtlistener-cli opinions list --limit 20
uv run courtlistener-cli opinions list --format xlsx --output ./results/
uv run courtlistener-cli opinions get 106359
uv run courtlistener-cli opinions count --search "miranda"
```

| Sub-command | Description |
|---|---|
| `list` | Paginated list; filters: `--search` |
| `get <id>` | Single opinion by ID |
| `count` | Total matching count only |

---

### clusters

Opinion clusters — groups of decisions (majority, dissent, concurrence) for a single case.

```bash
uv run courtlistener-cli clusters list --court scotus --limit 10
uv run courtlistener-cli clusters list --docket-number 23A994 --court scotus
uv run courtlistener-cli clusters list --date-filed-after 2020-01-01 --date-filed-before 2024-12-31
uv run courtlistener-cli clusters get 2812209
uv run courtlistener-cli clusters count --court scotus
```

| Option | Description |
|---|---|
| `--docket INTEGER` | Filter by docket ID |
| `--docket-number TEXT` | Filter by docket number |
| `--court TEXT` | Filter by court ID (e.g. `scotus`, `dcd`) |
| `--date-filed-after DATE` | ISO-8601 date lower bound |
| `--date-filed-before DATE` | ISO-8601 date upper bound |
| `--order-by TEXT` | Sort field; prefix `-` for descending |

> **Note:** The cluster ID in the URL `courtlistener.com/opinion/2812209/...` maps directly to `clusters get 2812209`.

---

### dockets

Top-level case metadata. Used for both case law and PACER data.

```bash
uv run courtlistener-cli dockets list --court dcd --limit 50
uv run courtlistener-cli dockets list --docket-number "1:16-cv-00745" --court dcd
uv run courtlistener-cli dockets list --date-filed-after 2023-01-01 --format xlsx
uv run courtlistener-cli dockets get 4214664
uv run courtlistener-cli dockets count --court scotus
```

**Batch mode** — supply a spreadsheet column of docket numbers:

```bash
uv run courtlistener-cli dockets list data/dockets.xlsx --column docketNumber --limit 50
uv run courtlistener-cli dockets list data/dockets.csv  --column docketNumber --court dcd --limit 0 --max-pages 0
```

Results include a `_query_value` column tracing which input row triggered each result.

| Option | Description |
|---|---|
| `--court TEXT` | Filter by court ID |
| `--docket-number TEXT` | Filter by docket number |
| `--case-name TEXT` | Filter by case name |
| `--date-filed-after DATE` | ISO-8601 lower bound |
| `--date-filed-before DATE` | ISO-8601 upper bound |

---

### docket-entries

Rows on a PACER docket. Each entry contains one or more RECAP documents.

```bash
uv run courtlistener-cli docket-entries list --docket 4214664 --limit 100
uv run courtlistener-cli docket-entries list --docket 4214664 --limit 0 --max-pages 0 --format xlsx
uv run courtlistener-cli docket-entries get 987654
```

`--docket` is required for `list` — filtering to a docket is the practical use case.

---

### recap-documents

Individual PDFs and attachments within PACER docket entries.

```bash
# List available documents for a docket entry
uv run courtlistener-cli recap-documents list --docket-entry 123456

# Only documents we have on file
uv run courtlistener-cli recap-documents list --docket-entry 123456 --is-available true

# Check if specific PACER document IDs are in RECAP
uv run courtlistener-cli recap-documents query \
  --court dcd \
  --pacer-doc-id 04505578698,04505578717
```

> `plain_text` is excluded by default — include it only when needed, as it significantly increases response size and latency.

> `recap-documents query` is only available to select users. Contact CourtListener to request access.

---

### parties

PACER case parties (plaintiffs, defendants, etc.) with nested attorney information.

```bash
uv run courtlistener-cli parties list --docket 4214664
uv run courtlistener-cli parties list --docket 4214664 --filter-nested-results
uv run courtlistener-cli parties list --docket 4214664 --format xlsx
```

| Option | Description |
|---|---|
| `--docket INTEGER` | Filter to parties in this docket |
| `--filter-nested-results` | Also filter nested attorney data to the same docket (off by default) |

---

### attorneys

PACER case attorneys with nested party representations.

```bash
uv run courtlistener-cli attorneys list --docket 4214664
uv run courtlistener-cli attorneys list --docket 4214664 --filter-nested-results
uv run courtlistener-cli attorneys get 9247906
```

Same `--filter-nested-results` semantics as `parties`.

---

### people

Judges, appointers, and other persons in the judiciary.

```bash
uv run courtlistener-cli people list --limit 20
uv run courtlistener-cli people list --name Smith --format xlsx
uv run courtlistener-cli people list --educations-school-name Rochester
uv run courtlistener-cli people get 1213
uv run courtlistener-cli people count --name Ginsburg
```

| Option | Description |
|---|---|
| `--name TEXT` | Filter by name (partial match via `__contains`) |
| `--educations-school-name TEXT` | Filter by law school name |
| `--has-photo BOOL` | Filter to judges with/without photos |

> Records where `is_alias_of` is non-null are nickname aliases — the `list` command filters to real person records by default.

---

### positions

Judicial positions held by people (judge, president, private practice, etc.).

```bash
uv run courtlistener-cli positions list --person 1213
uv run courtlistener-cli positions list --court scotus --limit 50
uv run courtlistener-cli positions get 42
```

---

### courts

Court metadata. Changes rarely — safe to cache locally.

```bash
uv run courtlistener-cli courts list --limit 0 --max-pages 0 --format xlsx
uv run courtlistener-cli courts list --jurisdiction FD   # federal district courts
uv run courtlistener-cli courts get scotus
uv run courtlistener-cli courts count --jurisdiction FD
```

---

### audio

Oral argument recordings — the largest collection on the internet, converted to optimized MP3.

```bash
uv run courtlistener-cli audio list --court scotus --limit 20
uv run courtlistener-cli audio list --date-argued-after 2023-01-01 --format xlsx
uv run courtlistener-cli audio get 98765
uv run courtlistener-cli audio count --court ca9 --year 2022
```

Fields of note: `local_path_mp3` (CourtListener-enhanced MP3), `download_url` (original court URL, may be taken down), `duration` (seconds, estimated).

---

### search

Full-text search across the entire CourtListener corpus — powered by a search engine, not the database.

```bash
# Case law (default)
uv run courtlistener-cli search query --q '"miranda rights"' --limit 50

# PACER dockets
uv run courtlistener-cli search query --q "apple inc" --type d --limit 20

# PACER filing documents
uv run courtlistener-cli search query --q '"serial number" firearm' --type r --format xlsx

# Judges
uv run courtlistener-cli search query --q "Ginsburg" --type p

# Oral arguments
uv run courtlistener-cli search query --q "commerce clause" --type oa

# Count only (no data export)
uv run courtlistener-cli search count --q '"gun control"' --type o
```

| `--type` | Result set |
|---|---|
| `o` | Case law opinions (default) |
| `d` | PACER dockets |
| `r` | PACER filing documents |
| `p` | Judges and people |
| `oa` | Oral argument audio |

Field names in search results use camelCase (e.g. `caseName`, `docketNumber`). The `snippet` field contains `<mark>`-tagged match highlights.

Full guide: [`docs/SEARCH_TYPES.md`](docs/SEARCH_TYPES.md)

---

### financial

Financial disclosure records for federal judges under the Ethics in Government Act. Used by WSJ and ProPublica for award-winning reporting.

```bash
# Main disclosures for a judge
uv run courtlistener-cli financial list --person 1213 --format xlsx

# Single disclosure
uv run courtlistener-cli financial get 34187

# Investment holdings (with value codes)
uv run courtlistener-cli financial investments --person 1213
uv run courtlistener-cli financial investments --gross-value-code P4   # investments >$50M
uv run courtlistener-cli financial investments --redacted true          # rows with redactions

# Gifts, debts, agreements, income
uv run courtlistener-cli financial gifts --disclosure 34187
uv run courtlistener-cli financial debts --disclosure 34187
uv run courtlistener-cli financial agreements --disclosure 34187
uv run courtlistener-cli financial non-investment-incomes --disclosure 34187

# Outside positions held (officer, director, trustee)
uv run courtlistener-cli financial disclosure-positions --disclosure 34187
```

| Sub-command | API path | Description |
|---|---|---|
| `list` / `get` | `/financial-disclosures/` | Main disclosure document |
| `investments` | `/investments/` | Investment income; supports `--gross-value-code`, `--redacted` |
| `gifts` | `/gifts/` | Gifts received (>$415) |
| `debts` | `/debts/` | Liabilities |
| `agreements` | `/agreements/` | Agreements and arrangements |
| `non-investment-incomes` | `/non-investment-incomes/` | Earned income (>$200) |
| `disclosure-positions` | `/disclosure-positions/` | Outside officer/director/trustee roles |

> **Value codes:** Monetary fields use coded ranges (e.g. `J` = $1–$15,000, `P4` = >$50M). See any PDF filing or issue an OPTIONS request to decode them.

---

### alerts

Search alerts — get email or webhook notifications when new matching results appear.

```bash
# List your alerts
uv run courtlistener-cli alerts list

# Create a real-time alert for new Apple Inc. opinions
uv run courtlistener-cli alerts create \
  --name "Apple Inc opinions" \
  --query 'q=%22Apple%20Inc%22&type=o' \
  --rate rt

# Create a daily RECAP alert for new filings in Apple cases
uv run courtlistener-cli alerts create \
  --name "Apple RECAP" \
  --query 'q=%22Apple%22&type=r' \
  --rate dly \
  --alert-type r

# Update frequency
uv run courtlistener-cli alerts update --id 4839 --rate wly

# Delete
uv run courtlistener-cli alerts delete --id 4839 --confirm
```

| `--rate` | Frequency |
|---|---|
| `rt` | Real-time (webhook always real-time regardless) |
| `dly` | Daily digest |
| `wly` | Weekly digest |
| `mly` | Monthly digest |

> For RECAP search alerts, `--alert-type d` sends notifications for new cases only; `--alert-type r` includes new filings.

---

### docket-alerts

Subscribe to updates for specific dockets. Notified immediately when new information arrives.

```bash
# Subscribe to a docket
uv run courtlistener-cli docket-alerts create --docket 4214664

# List subscriptions
uv run courtlistener-cli docket-alerts list

# Unsubscribe
uv run courtlistener-cli docket-alerts delete --id 133013 --confirm
```

---

### citation-lookup

Verify legal citations against CourtListener's database of 18M+ citations. Useful for detecting AI-hallucinated citations.

```bash
# Scan a block of text for all citations
uv run courtlistener-cli citation-lookup text \
  --text "Obergefell v. Hodges (576 U.S. 644) established the right to marriage."

# Look up a specific citation
uv run courtlistener-cli citation-lookup citation \
  --volume 576 --reporter "U.S." --page 644
```

Response fields: `citation`, `normalized_citations` (corrects typos/non-canonical abbreviations), `status` (200=found, 404=not found, 300=ambiguous, 400=invalid reporter), `clusters` (matching cluster objects).

**Limits:** 250 citations per request · 60 valid citations/minute · 64,000 characters max per text request.

Does not look up statutes, `id.`, or `supra` citations.

---

### tags

User-created tags linked to dockets.

```bash
uv run courtlistener-cli tags list
uv run courtlistener-cli tags get 1316
```

---

### batch

Process arbitrary API requests from a CSV or JSON Lines file.

```bash
uv run courtlistener-cli batch --input-file data/batch.csv --format xlsx
uv run courtlistener-cli batch --input-file data/batch.jsonl --output-path ./results/
```

Input CSV format:

```csv
method,endpoint
GET,/opinions/?limit=5
GET,/courts/scotus/
```

---

## Output Formats

| Format | Use case |
|---|---|
| `json` | Full structured data, nested objects preserved |
| `csv` | Tabular; nested dicts auto-flattened to dot-notation keys |
| `xlsx` | Excel workbooks with formatted headers |

Filenames include a timestamp by default (`YYYYMMDD_HHMMSS`). Disable with `INCLUDE_TIMESTAMP=false`.

---

## Rate Limits

CourtListener's default limits for authenticated users:

| Window | Limit |
|---|---|
| Per minute | 5 requests |
| Per hour | 50 requests |
| Per day | 125 requests |

The CLI automatically retries on 429 using the `Retry-After` header. If the wait exceeds 5 minutes, it raises `DailyQuotaExceeded` with a human-readable time estimate rather than looping overnight.

Weekly maintenance window: **Thursday 21:00–23:59 PT**.

---

## Search Pagination Examples

```bash
# Default: up to 10 pages, no row cap
uv run courtlistener-cli search query --q '"serial number" firearm' --limit 0 --format json

# Exactly 25 results across however many pages needed
uv run courtlistener-cli search query --q '"serial number" firearm' --limit 25 --format xlsx

# Unbounded — fetch everything (use with care on large result sets)
uv run courtlistener-cli search query --q '"serial number" firearm' --limit 0 --max-pages 0
```

---

## Development

```bash
make install-dev    # editable install with dev extras
make lint           # ruff check --fix + ruff format
make test           # pytest -v --tb=short
make run            # display CLI help
make help           # all available targets
```

---

## API Documentation

- [CourtListener API overview](https://www.courtlistener.com/help/api/rest/)
- [PRD reference](courtlistener_cli_PRD.md) — full endpoint inventory with filters and field notes

## License

CC0 1.0 Universal (same as CourtListener data)
