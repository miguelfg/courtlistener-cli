# CourtListener CLI — Product Requirements Document

## Table of Contents

1. [Introduction](#introduction)
2. [Implementation Decisions](#implementation-decisions)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Authentication](#authentication)
6. [Endpoint Reference](#endpoint-reference)
7. [Input/Output Examples](#inputoutput-examples)
8. [Rate Limiting](#rate-limiting)
9. [Error Handling](#error-handling)
10. [Logging](#logging)
11. [Best Click Practices](#best-click-practices)
12. [Makefile & Project Management](#makefile--project-management)
13. [Implementation Checklist](#implementation-checklist)

---

## Introduction

### Overview

This document describes the Product Requirements for a Python CLI client for the **CourtListener REST API v4** operated by the Free Law Project. The client provides a command-line interface for querying case law, PACER federal court filings, judges, oral arguments, financial disclosures, citations, and legal alerts.

**Base URL:** `https://www.courtlistener.com/api/rest/v4`

**Resources:** `search, dockets, docket-entries, recap-documents, parties, attorneys, clusters, opinions, courts, audio, people, positions, financial-disclosures, investments, gifts, debts, alerts, docket-alerts, citation-lookup, tags`

### Purpose

- Enable journalists, researchers, and developers to query CourtListener's legal database from the command line
- Support batch operations for large-scale data extraction (e.g., searching by lists of docket numbers or case names)
- Provide exportable outputs in XLSX, CSV, and JSON for analysis and reporting pipelines
- Implement best practices for API interactions (retry on 429, rate limit handling, cursor pagination)

### Target Audience

- Data journalists and researchers at organizations like ICIJ processing large volumes of court data
- Empirical legal researchers building case law corpora
- Developers integrating CourtListener data into pipelines

### Key Features

- ✓ Full coverage of CourtListener API v4 resources
- ✓ Multiple output formats (JSON, CSV, XLSX)
- ✓ Batch processing (CSV/XLSX input for bulk queries)
- ✓ Automatic retry with exponential backoff on 429 / daily quota detection
- ✓ Cursor-based pagination with configurable row cap and page cap
- ✓ Rate limiting awareness (5 req/min, 50/hr, 125/day by default)
- ✓ Comprehensive logging for debugging

---

## Implementation Decisions

- CLI Name: `courtlistener-cli`
- Python Version: `>=3.10`
- HTTP Library: `httpx`
- Authentication: `Token authentication — Authorization: Token <api-token>` (derived from API docs)
- Credentials Configuration: `env_vars`
- Timeout: `30s total timeout` (configurable via `COURTLISTENER_TIMEOUT`)
- Retry Policy: Enabled: `5 attempts`, respects `Retry-After` header on 429; raises `DailyQuotaExceeded` when `Retry-After > 300s`; status codes `408,429,500,502,503,504`
- Output Formats: `json,csv,xlsx`
- Output Accepted Formats and Default: `default_xlsx__accepted_xlsx_csv`
- Batch Input Formats: `csv` (plus XLSX for structured batch lookups)
- Default Save Data Mode: `timestamped`
- Lint/Format Toolchain: `ruff check --fix` + `ruff format`

---

## Installation

### System Requirements

- Python 3.10+
- `uv` (recommended Python package/project manager)

### Recommended (uv)

```bash
git clone <repo>
cd courtlistener-cli
uv sync
```

### Alternative (pip)

```bash
pip install -e .
```

### Verify Installation

```bash
uv run courtlistener-cli --version
uv run courtlistener-cli --help
```

### Validation Requirements

The generated CLI project must include live smoke validation for read-oriented commands:
- Run low-volume GET/list validation for each read/list command.
- Use `--limit 10` (maps to the `page_size` or `limit` query parameter) to cap returned records.
- Prefer commands that do not require fabricated identifiers (use list endpoints, not get-by-ID).
- Treat these live read validations as required acceptance checks, not optional extras.

### Dependencies

- **httpx** ≥ 0.27 — HTTP client
- **click** ≥ 8.1.0 — CLI framework
- **pandas** ≥ 1.5.0 — Data manipulation
- **openpyxl** ≥ 3.1.0 — XLSX read/write
- **python-dotenv** ≥ 1.0.0 — Environment configuration

---

## Configuration

### Environment Variables

```bash
# Required
COURTLISTENER_API_TOKEN=your-token-here

# Optional — all have defaults
COURTLISTENER_BASE_URL=https://www.courtlistener.com/api/rest/v4
COURTLISTENER_TIMEOUT=30
LOG_LEVEL=DEBUG
LOG_TO_FILE=false
OUTPUT_FORMAT=xlsx
INCLUDE_TIMESTAMP=true
```

### Priority Order

1. CLI flags (highest)
2. Environment variables
3. `.env` file loaded by python-dotenv
4. Hardcoded defaults (lowest)

### `.env` File

Copy `.env.example` to `.env` and fill in `COURTLISTENER_API_TOKEN`.

---

## Authentication

### Token Authentication (Required)

CourtListener uses Token authentication. Without a token, many endpoints are accessible but rate limits are more restrictive; token authentication is required for monitoring and quota expansion.

```
Authorization: Token <your-token-here>
```

Example:
```bash
export COURTLISTENER_API_TOKEN=abc123...
uv run courtlistener-cli dockets list --limit 10
```

The token is obtained by creating a CourtListener account and visiting the API settings page.

### Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 401 | Invalid or missing token | Display error with setup hint |
| 403 | Insufficient permissions (select-user endpoint) | Display error message |
| 429 | Rate limited | Automatic retry with `Retry-After` backoff; raise `DailyQuotaExceeded` when `Retry-After > 300s` |

### Best Practices

- Store token in `.env` or environment variable — never hardcode
- The token is a long-lived credential; rotate if compromised
- Multiple accounts per project/person are forbidden by CourtListener's TOS

---

## Endpoint Reference

### API Pagination

All list endpoints use **cursor-based pagination**. Responses include `next` and `previous` cursor URLs. The client's `paginate_endpoint()` function handles this automatically:

- `--limit N` — stop after N total rows
- `--max-pages N` — stop after N pages (no row cap)
- Neither flag — fetch all pages until `next` is `null`

Response envelope:
```json
{
  "count": 123456,
  "next": "https://...?cursor=xxx",
  "previous": null,
  "results": [...]
}
```

### Filtering

Filters use Django-style field lookups via query parameters (double underscores for related fields):
- `?court=scotus` — exact court match
- `?id__gt=500&id__lt=1000` — range filter
- `?docket_number=23A994` — docket number match
- `?cluster__docket__court=scotus` — cross-resource join filter
- `?court__jurisdiction!=F` — exclusion filter (prepend `!`)

### Ordering

Use `?order_by=field` (ascending) or `?order_by=-field` (descending). Multiple fields with comma separation. Always add a secondary `id` sort when ordering by a non-unique field to ensure stable pagination.

### Field Selection

Use `?fields=field1,field2` to reduce payload. Use `?fields!=field1` to exclude fields. Strongly recommended for `plain_text` and `html_*` fields on opinions.

---

### SEARCH Resource

**Base path:** `/api/rest/v4/search/`

Full-text search across the CourtListener corpus. Unlike other endpoints, this is powered by a search engine (not the database), so filtering uses query parameters, not OPTIONS-discoverable field lookups.

#### 1. Search

- Command: `courtlistener-cli search query`
- Method: GET
- Path: `/api/rest/v4/search/`
- Description: Full-text search across case law, PACER filings, judges, or oral arguments
- Key Parameters:
  - `--q TEXT` — search query (supports Lucene-style operators)
  - `--type TEXT` — result type: `o` (opinions), `r` (PACER filings), `d` (PACER dockets), `p` (people/judges), `oa` (oral arguments) [default: `o`]
  - `--order-by TEXT` — sort field
  - `--limit N` — row cap
  - `--output-file PATH` — save to file
  - `--format TEXT` — output format (xlsx, csv, json)
- Notes: camelCase field names (e.g., `caseName`, `docketNumber`). Snippet field contains `<mark>`-tagged matches.
- Response Example:
  ```json
  {
    "count": 2369,
    "next": "https://...?page=2&q=foo",
    "results": [
      {
        "id": 106359,
        "caseName": "Fong Foo v. United States",
        "court": "Supreme Court of the United States",
        "dateFiled": "1962-03-19T00:00:00-08:00",
        "status": "Precedential",
        "snippet": "...<mark>foo</mark>..."
      }
    ]
  }
  ```

---

### DOCKETS Resource

**Base path:** `/api/rest/v4/dockets/`

Dockets are the top of the object hierarchy — linking docket entries, parties, attorneys (PACER), clusters of opinions (case law), and audio files (oral arguments).

#### 1. List Dockets

- Command: `courtlistener-cli dockets list`
- Method: GET
- Path: `/api/rest/v4/dockets/`
- Key Parameters:
  - `--court TEXT` — filter by court ID (e.g., `scotus`, `dcd`)
  - `--docket-number TEXT` — filter by docket number
  - `--case-name TEXT` — filter by case name
  - `--date-filed-after DATE` — ISO-8601 date filter
  - `--date-filed-before DATE`
  - `--order-by TEXT` — e.g., `-date_filed`
  - `--limit N`, `--max-pages N`, `--output-file PATH`, `--format TEXT`

#### 2. Get Docket by ID

- Command: `courtlistener-cli dockets get`
- Method: GET
- Path: `/api/rest/v4/dockets/{id}/`
- Parameters: `--id INTEGER` (required)

---

### DOCKET-ENTRIES Resource

**Base path:** `/api/rest/v4/docket-entries/`

Rows on a PACER docket. Each entry contains one or more RECAP documents.

#### 1. List Docket Entries

- Command: `courtlistener-cli docket-entries list`
- Method: GET
- Path: `/api/rest/v4/docket-entries/`
- Key Parameters:
  - `--docket INTEGER` — filter to a specific docket (required in most use cases)
  - `--limit N`, `--max-pages N`, `--output-file PATH`, `--format TEXT`

#### 2. Get Docket Entry

- Command: `courtlistener-cli docket-entries get`
- Method: GET
- Path: `/api/rest/v4/docket-entries/{id}/`

---

### RECAP-DOCUMENTS Resource

**Base path:** `/api/rest/v4/recap-documents/`

Individual documents (PDFs, attachments) within PACER docket entries.

#### 1. List RECAP Documents

- Command: `courtlistener-cli recap-documents list`
- Method: GET
- Path: `/api/rest/v4/recap-documents/`
- Notes: Omit `plain_text` via field selection unless required — it is large and slows responses.
- Key Parameters:
  - `--docket-entry INTEGER` — filter by docket entry
  - `--is-available BOOL` — filter to documents available in RECAP
  - `--limit N`, `--output-file PATH`, `--format TEXT`

#### 2. Fast Document Lookup (RECAP Query)

- Command: `courtlistener-cli recap-documents query`
- Method: GET
- Path: `/api/rest/v4/recap-query/`
- Description: Check if PACER documents with known IDs are in the RECAP archive
- Parameters:
  - `--court TEXT` — court ID (required)
  - `--pacer-doc-id TEXT` — comma-separated PACER doc IDs (up to 300)
- Notes: PACER doc IDs are normalized to zero in the 4th digit. This endpoint is only available to select users.

---

### PARTIES Resource

**Base path:** `/api/rest/v4/parties/`

Parties in PACER cases, with nested attorney information.

#### 1. List Parties

- Command: `courtlistener-cli parties list`
- Method: GET
- Path: `/api/rest/v4/parties/`
- Key Parameters:
  - `--docket INTEGER` — filter to a specific docket
  - `--filter-nested-results BOOL` — filter nested attorney data to match the docket filter
  - `--limit N`, `--output-file PATH`, `--format TEXT`

---

### ATTORNEYS Resource

**Base path:** `/api/rest/v4/attorneys/`

Attorneys in PACER cases.

#### 1. List Attorneys

- Command: `courtlistener-cli attorneys list`
- Method: GET
- Path: `/api/rest/v4/attorneys/`
- Key Parameters:
  - `--docket INTEGER` — filter to a specific docket
  - `--filter-nested-results BOOL` — filter nested party data
  - `--limit N`, `--output-file PATH`, `--format TEXT`

---

### CLUSTERS Resource

**Base path:** `/api/rest/v4/clusters/`

Opinion clusters group together the decisions (majority, dissent, concurrence) from a single case hearing.

#### 1. List Clusters

- Command: `courtlistener-cli clusters list`
- Method: GET
- Path: `/api/rest/v4/clusters/`
- Key Parameters:
  - `--docket INTEGER` — filter by docket
  - `--docket-docket-number TEXT` — filter by docket number (`docket__docket_number`)
  - `--court TEXT` — filter via join (`docket__court`)
  - `--date-filed-after DATE`, `--date-filed-before DATE`
  - `--limit N`, `--output-file PATH`, `--format TEXT`

#### 2. Get Cluster by ID

- Command: `courtlistener-cli clusters get`
- Method: GET
- Path: `/api/rest/v4/clusters/{id}/`
- Note: The cluster ID matches the opinion cluster URL on the CourtListener website.

---

### OPINIONS Resource

**Base path:** `/api/rest/v4/opinions/`

Contains the text and metadata of individual judicial decisions.

#### 1. List Opinions

- Command: `courtlistener-cli opinions list`
- Method: GET
- Path: `/api/rest/v4/opinions/`
- Key Parameters:
  - `--cluster INTEGER` — filter by cluster
  - `--cluster-docket-court TEXT` — filter by court via join
  - `--cluster-docket-docket-number TEXT`
  - `--fields TEXT` — use field selection to omit `html_*` / `plain_text` unless needed
  - `--limit N`, `--output-file PATH`, `--format TEXT`
- Notes:
  - Prefer `html_with_citations` over `plain_text` for opinion text.
  - `plain_text` is large; always exclude it with `?fields!=plain_text` unless explicitly requested.
  - Opinion IDs do not reliably match cluster IDs.

#### 2. Get Opinion by ID

- Command: `courtlistener-cli opinions get`
- Method: GET
- Path: `/api/rest/v4/opinions/{id}/`

---

### COURTS Resource

**Base path:** `/api/rest/v4/courts/`

Metadata about courts. Changes rarely — safe to cache.

#### 1. List Courts

- Command: `courtlistener-cli courts list`
- Method: GET
- Path: `/api/rest/v4/courts/`
- Key Parameters:
  - `--jurisdiction TEXT` — filter by jurisdiction code (e.g., `FD` for federal district)
  - `--limit N`, `--output-file PATH`, `--format TEXT`

#### 2. Get Court by ID

- Command: `courtlistener-cli courts get`
- Method: GET
- Path: `/api/rest/v4/courts/{id}/`

---

### AUDIO Resource

**Base path:** `/api/rest/v4/audio/`

Oral argument recordings. The largest collection on the internet, converted to optimized MP3.

#### 1. List Audio Files

- Command: `courtlistener-cli audio list`
- Method: GET
- Path: `/api/rest/v4/audio/`
- Key Parameters:
  - `--docket INTEGER` — filter by docket
  - `--court TEXT`
  - `--date-argued-after DATE`, `--date-argued-before DATE`
  - `--limit N`, `--output-file PATH`, `--format TEXT`
- Notes:
  - `local_path_mp3` — path to the CourtListener-enhanced MP3 (preferred)
  - `download_url` — original court URL (may be taken down)
  - `duration` — estimated length in seconds (variable-bitrate estimate, not always accurate)

#### 2. Get Audio File

- Command: `courtlistener-cli audio get`
- Method: GET
- Path: `/api/rest/v4/audio/{id}/`

---

### PEOPLE Resource

**Base path:** `/api/rest/v4/people/`

Judges, appointers, and other persons in the judiciary.

#### 1. List People

- Command: `courtlistener-cli people list`
- Method: GET
- Path: `/api/rest/v4/people/`
- Key Parameters:
  - `--name TEXT` — filter by name (supports `__contains`, `__startswith`)
  - `--educations-school-name TEXT` — filter by school name (`educations__school__name__contains`)
  - `--has-photo BOOL`
  - `--limit N`, `--output-file PATH`, `--format TEXT`
- Notes:
  - Records where `is_alias_of` is non-null are nicknames — filter to `is_alias_of__isnull=True` for person records only.
  - `race` and `gender` fields are not self-reported; treat as best estimates.

#### 2. Get Person by ID

- Command: `courtlistener-cli people get`
- Method: GET
- Path: `/api/rest/v4/people/{id}/`

---

### POSITIONS Resource

**Base path:** `/api/rest/v4/positions/`

Judicial positions held by a person (judge, president, private practice, etc.).

#### 1. List Positions

- Command: `courtlistener-cli positions list`
- Method: GET
- Path: `/api/rest/v4/positions/`
- Key Parameters:
  - `--person INTEGER` — filter to positions for a specific person
  - `--court TEXT`
  - `--limit N`, `--output-file PATH`, `--format TEXT`

---

### FINANCIAL-DISCLOSURES Resource

**Base path:** `/api/rest/v4/financial-disclosures/`

Financial disclosure records of federal judges under the Ethics in Government Act.

#### 1. List Financial Disclosures

- Command: `courtlistener-cli financial-disclosures list`
- Method: GET
- Path: `/api/rest/v4/financial-disclosures/`
- Key Parameters:
  - `--person INTEGER` — filter by judge person ID
  - `--year INTEGER`
  - `--limit N`, `--output-file PATH`, `--format TEXT`

#### Sub-resources (all use same pattern)

| Command Group | Base Path | Description |
|---|---|---|
| `investments list` | `/api/rest/v4/investments/` | Investment income holdings |
| `disclosure-positions list` | `/api/rest/v4/disclosure-positions/` | Positions held (officer, director, etc.) |
| `agreements list` | `/api/rest/v4/agreements/` | Agreements or arrangements |
| `non-investment-incomes list` | `/api/rest/v4/non-investment-incomes/` | Non-investment earned income |
| `gifts list` | `/api/rest/v4/gifts/` | Gifts received |
| `debts list` | `/api/rest/v4/debts/` | Liabilities |

All sub-resources support `--financial-disclosure INTEGER` filter and standard `--limit`, `--output-file`, `--format` flags.

**Value Codes:** Investments, debts, and gifts use coded ranges (e.g., `J` = $1–$15,000) instead of exact values. Issue an OPTIONS request to see code mappings.

**Redacted fields:** Use `?redacted=True` to find rows with redacted data.

---

### ALERTS Resource

**Base path:** `/api/rest/v4/alerts/`

Search alerts that send email or webhook notifications for new matching results.

#### 1. List Search Alerts

- Command: `courtlistener-cli alerts list`
- Method: GET
- Path: `/api/rest/v4/alerts/`

#### 2. Create Search Alert

- Command: `courtlistener-cli alerts create`
- Method: POST
- Path: `/api/rest/v4/alerts/`
- Parameters:
  - `--name TEXT` — human-friendly name (required)
  - `--query TEXT` — URL-encoded query string from CourtListener front end (required)
  - `--rate TEXT` — `rt` | `dly` | `wly` | `mly` (required)
  - `--alert-type TEXT` — for RECAP: `d` (dockets only) or `r` (dockets + filings)

#### 3. Update Search Alert

- Command: `courtlistener-cli alerts update`
- Method: PATCH
- Path: `/api/rest/v4/alerts/{id}/`
- Parameters: `--id INTEGER` + any updatable field

#### 4. Delete Search Alert

- Command: `courtlistener-cli alerts delete`
- Method: DELETE
- Path: `/api/rest/v4/alerts/{id}/`
- Parameters: `--id INTEGER` + `--confirm`

---

### DOCKET-ALERTS Resource

**Base path:** `/api/rest/v4/docket-alerts/`

Subscribe to notifications for specific dockets.

#### 1–4. CRUD (same pattern as ALERTS)

- List: `courtlistener-cli docket-alerts list`
- Create: `--docket INTEGER` + optional `--alert-type INTEGER` (1=subscribe, 0=unsubscribe)
- Update: PATCH with `--alert-type`
- Delete: DELETE with `--id INTEGER --confirm`

---

### CITATION-LOOKUP Resource

**Base path:** `/api/rest/v4/citation-lookup/`

Look up legal citations in CourtListener's database of 18M+ citations. Useful for verifying citations and detecting AI hallucinations.

#### 1. Lookup Citations

- Command: `courtlistener-cli citation-lookup`
- Method: POST
- Path: `/api/rest/v4/citation-lookup/`
- Parameters (mutually exclusive modes):
  - `--text TEXT` — blob of text; all citations found within it are parsed and looked up
  - `--volume INTEGER --reporter TEXT --page TEXT` — look up a single citation by its components
- Response Fields:
  - `citation` — citation string
  - `normalized_citations` — canonical form(s), correcting typos or ambiguity
  - `start_index`, `end_index` — character offsets in the text
  - `status` — 200 (found), 404 (not found), 400 (invalid reporter), 300 (ambiguous), 429 (too many citations)
  - `clusters` — matching cluster objects
- Limits: 250 citations per request, 60 valid citations/minute, 64,000 characters max per request
- Notes: Does not look up statutes, `id.`, or `supra` citations. No filtering, pagination, or field selection.

---

### TAGS Resource

**Base path:** `/api/rest/v4/tag/`

User-created tags linked to dockets.

#### 1. List Tags

- Command: `courtlistener-cli tags list`
- Method: GET
- Path: `/api/rest/v4/tag/`
- Parameters: `--limit N`, `--output-file PATH`, `--format TEXT`

---

### BATCH Resource

The `batch` command group reads a column from a CSV or XLSX file and executes a parameterized query for each value.

#### 1. Batch Docket Query

- Command: `courtlistener-cli batch dockets`
- Description: Read docket numbers (or court+docket pairs) from a spreadsheet and retrieve matching dockets for each row
- Parameters:
  - `--input-file PATH` — CSV or XLSX input file
  - `--column TEXT` — column name containing the docket numbers
  - `--court TEXT` — optional court filter applied to all rows
  - `--output-file PATH`, `--format TEXT`
- Behavior: Appends `_query_value` column to each result row to trace which input triggered it

---

## Input/Output Examples

### Single Request — List SCOTUS Dockets

```bash
uv run courtlistener-cli dockets list \
  --court scotus \
  --limit 10 \
  --format xlsx \
  --output-file scotus_dockets.xlsx
```

### Search for Case Law

```bash
uv run courtlistener-cli search query \
  --q "gun control" \
  --type o \
  --limit 50 \
  --output-file gun_control_opinions.xlsx
```

### Citation Lookup

```bash
uv run courtlistener-cli citation-lookup \
  --volume 576 --reporter "U.S." --page 644
```

### Batch Docket Lookup from Spreadsheet

```bash
uv run courtlistener-cli batch dockets \
  --input-file dockets.xlsx \
  --column docket_number \
  --court dcd \
  --output-file dcd_results.xlsx
```

### Typical JSON Response (List Endpoint)

```json
{
  "count": 123456,
  "next": "https://www.courtlistener.com/api/rest/v4/dockets/?cursor=cD0x...",
  "previous": null,
  "results": [
    {
      "resource_uri": "https://www.courtlistener.com/api/rest/v4/dockets/4214664/",
      "id": 4214664,
      "court_id": "dcd",
      "case_name": "NATIONAL VETERANS LEGAL SERVICES PROGRAM v. United States",
      "docket_number": "1:16-cv-00745",
      "date_filed": "2016-04-21",
      "date_terminated": null
    }
  ]
}
```

---

## Rate Limiting

### API-Enforced Limits (Authenticated)

| Window | Limit |
|--------|-------|
| Per minute | 5 requests |
| Per hour | 50 requests |
| Per day | 125 requests |

Limits apply concurrently; the most restrictive applies. Commercial partnerships and Free Law Project memberships expand quota.

### Maintenance Window

Weekly downtime: **Thursday 21:00–23:59 PT**.

### Client Behavior

- On HTTP 429: read `Retry-After` header; wait and retry (up to 5 attempts).
- If `Retry-After > 300s`: raise `DailyQuotaExceeded` — do not retry, notify user with wait time.
- Between paginated requests: no enforced client-side delay, but log 429 occurrences prominently.

### Configuration

| Env Var | Default | Purpose |
|---------|---------|---------|
| `COURTLISTENER_TIMEOUT` | `30` | Request timeout (seconds) |
| (internal) `_MAX_RETRIES` | `5` | Max retry attempts |
| (internal) `_DEFAULT_RETRY_WAIT` | `60` | Wait when no Retry-After header |
| (internal) `_MAX_RETRY_WAIT` | `300` | Threshold for daily quota detection |

---

## Error Handling

### Error Classification

| Status | Type | Action |
|--------|------|--------|
| 400 | Client error (bad request) | Display error, do not retry |
| 401 | Auth error | Display error with token setup hint |
| 403 | Permission error | Display error (select-user API) |
| 404 | Not found | Display error with resource ID |
| 429 | Rate limited | Retry with `Retry-After`; raise `DailyQuotaExceeded` if long wait |
| 500, 502, 503, 504 | Server error | Retry with exponential backoff |
| Network timeout | Connection error | Retry up to `_MAX_RETRIES` |

### Non-JSON Responses

The API can return HTML (browser Accept header) or XML. Always request JSON explicitly via the `Accept: application/json` header or check `Content-Type` before calling `.json()`.

### Common Errors

| Error | Solution |
|-------|----------|
| Token missing | `export COURTLISTENER_API_TOKEN=...` |
| Daily quota exceeded | Wait; see `DailyQuotaExceeded.wait` for exact seconds |
| Deep pagination slow | Use date-range slicing (`?date_filed__gte=...&date_filed__lt=...`) |
| `opinion.plain_text` slow | Add `?fields!=plain_text` to exclude it |

### Best Practices

- Catch `DailyQuotaExceeded` separately from generic 429 — it needs hours not seconds.
- Never retry on 400, 401, 403, 404.
- Validate and normalize the base URL join to avoid double slashes.
- Handle empty or partial responses before calling `.json()`.

---

## Logging

### Log Levels

| Level | Used For |
|-------|---------|
| DEBUG | Full request URL, headers, response payloads |
| INFO | API calls, pagination progress, timing |
| WARNING | 429 retries, slow page numbers, deprecated endpoints |
| ERROR | Auth failures, `DailyQuotaExceeded`, unrecoverable HTTP errors |

### Configuration

```bash
# Via environment variable
export LOG_LEVEL=DEBUG
export LOG_TO_FILE=true  # writes to courtlistener-cli.log
```

### Log Format

```
2024-01-15 10:30:45,123 - courtlistener_cli - INFO - GET /dockets/ page=1 (0.45s, rows=100)
2024-01-15 10:30:46,234 - courtlistener_cli - WARNING - Rate limited (429). Waiting 60s before retry 1/5…
```

---

## Best Click Practices

### Command Structure

```
courtlistener-cli <resource> <action> [OPTIONS]
```

- Use `--flag` options, not positional arguments
- Group commands by resource: `dockets list`, `dockets get`
- Provide `--help` at every level

### Standard Options (All Commands)

```
--format TEXT          Output format: xlsx, csv, json [default: xlsx]
--output-file PATH     Save output to file (if omitted, print to stdout)
--api-token TEXT       Override COURTLISTENER_API_TOKEN
--verbose              Enable verbose/debug output
```

### Standard Options (List Commands)

```
--limit N              Max total rows to retrieve (0 = unlimited)
--max-pages N          Max pages to fetch (0 = unlimited)
--order-by TEXT        Sort field (prefix - for descending)
--fields TEXT          Comma-separated list of fields to include
```

### Destructive Commands (alerts delete, docket-alerts delete)

```
--confirm              Required flag to confirm deletion
```

---

## Makefile & Project Management

### Project Structure

```
courtlistener-cli/
├── Makefile
├── pyproject.toml
├── uv.lock
├── .env.example
├── .env                  # gitignored
├── src/
│   ├── cli.py            # Click entry point; registers all command groups
│   ├── client.py         # CourtListenerClient — httpx wrapper with Token auth
│   ├── config.py         # Singleton Config; loads .env via python-dotenv
│   ├── pagination.py     # paginate_endpoint() — cursor-based pagination logic
│   ├── output.py         # save_json/csv/xlsx + flatten_dict
│   ├── batch_processor.py
│   └── commands/
│       ├── search_commands.py
│       ├── dockets_commands.py
│       ├── opinions_commands.py
│       ├── courts_commands.py
│       ├── people_commands.py
│       ├── audio_commands.py
│       ├── alerts_commands.py
│       ├── financial_commands.py
│       └── ...
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   └── test_client.py
└── docs/
    ├── SEARCH_TYPES.md
    └── api/
```

### Makefile Targets

```bash
make install           # uv sync
make install-dev       # uv sync --all-extras
make lint              # ruff check --fix + ruff format
make test              # pytest -v --tb=short
make run               # display CLI help

# Smoke-test targets (low-volume live validation)
make dockets-list      # uv run courtlistener-cli dockets list --limit 10
make courts-list       # uv run courtlistener-cli courts list --limit 10
make opinions-list     # uv run courtlistener-cli opinions list --limit 10
make audio-list        # uv run courtlistener-cli audio list --limit 10
make people-list       # uv run courtlistener-cli people list --limit 10
make search-sample     # uv run courtlistener-cli search query --q "test" --limit 5
make alerts-list       # uv run courtlistener-cli alerts list
```

---

## Implementation Checklist

- [ ] Do not shadow imported class/function names (e.g., avoid redefining `Config` in a module that imports it).
- [ ] Ensure all advertised output formats are fully implemented (`json`, `csv`, `xlsx`) for both single and batch commands.
- [ ] Use `Authorization: Token <token>` header (not `Bearer`).
- [ ] Parse cursor from `next` field, not from page numbers, for pagination.
- [ ] Raise `DailyQuotaExceeded` (not a generic 429 error) when `Retry-After > 300s`.
- [ ] Use `?fields!=plain_text` by default for opinion list commands; only include text fields when explicitly requested.
- [ ] Handle `is_alias_of` on People — filter to `is_alias_of__isnull=True` by default.
- [ ] For Parties and Attorneys endpoints, expose `--filter-nested-results` flag.
- [ ] Citation Lookup is a POST endpoint — do not implement as GET.
- [ ] Financial sub-resource endpoints (`investments`, `gifts`, `debts`, etc.) must filter by `--financial-disclosure INTEGER`.
- [ ] RECAP Query (`/recap-query/`) endpoint normalizes the 4th digit of `pacer_doc_id` to zero.
- [ ] Avoid deep pagination without date-range slicing; document the performance warning.
- [ ] Define file I/O with explicit UTF-8 encoding and CSV-safe writes.
- [ ] Handle non-JSON / empty API responses safely before calling `.json()`.
- [ ] Add integration/smoke tests that verify generated files and CLI behavior end-to-end.
- [ ] Ensure `pyproject.toml` is complete with console script entry point and all dependencies.
- [ ] `prd-to-cli` must run low-volume live validation (`--limit 10`) against each generated list command.

---

## Handoff

To scaffold the project from this PRD:

```
/prd-to-cli @courtlistener_cli_PRD.md ./
```

The existing codebase already implements: `opinions`, `search`, `dockets`, `courts`, `people`, `audio`, and `batch` command groups. The following resources are **not yet implemented** and are candidates for the next generation pass:

- `docket-entries`, `recap-documents` (PACER document layer)
- `parties`, `attorneys`
- `clusters` (as a standalone command — currently traversed via dockets)
- `positions`, `political-affiliations`, `educations` (judge sub-resources)
- `financial-disclosures` and all sub-resources
- `alerts`, `docket-alerts`
- `citation-lookup`
- `tags`
- `originating-court-information`, `bankruptcy-information`, `fjc-integrated-database`
