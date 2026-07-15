---
name: courtlistener-cli
description: This skill should be used when running, querying, or analyzing results from the courtlistener-cli tool — a Python Click CLI for the CourtListener REST API v4 (case law opinions, PACER dockets/entries/documents, parties, attorneys, judges, financial disclosures, oral arguments, search, alerts, citation lookup). Covers setup, every command and its parameters, rate-limit-aware query planning, batch processing, and post-processing exported JSON/CSV/XLSX results into stats and insights.
---

# CourtListener CLI

Run and analyze queries against the CourtListener API through this repo's CLI.

## Running the CLI

Resolve the installation directory first, in this order:

1. `$COURTLISTENER_CLI_HOME` if set
2. Otherwise the repo root containing this skill (`.claude/skills/courtlistener-cli` → three levels up)

Then invoke through uv from that directory:

```bash
cd "$CLI_HOME" && uv run courtlistener-cli <group> <command> [options]
```

If it fails with a missing module, run `make install` in that directory first.
Never install the CLI, a venv, or a repo clone under this skill folder — it is
documentation only; anything created here anyway is gitignored.

## Command reference

The full `--help` output of every command and sub-command (18 groups, all
options) is in [`references/commands.md`](references/commands.md). Grep it
before composing any command — do not guess option names:

```bash
grep -A 30 '`courtlistener-cli dockets list`' .claude/skills/courtlistener-cli/references/commands.md
```

Groups: `opinions`, `clusters`, `dockets`, `docket-entries`, `recap-documents`,
`parties`, `attorneys`, `people`, `positions`, `courts`, `audio`, `search`,
`financial`, `alerts`, `docket-alerts`, `citation-lookup`, `tags`, `batch`.

If a command errors with an unknown option, the reference may be stale — check
`uv run courtlistener-cli <group> <cmd> --help` and regenerate the reference.

## Setup and config

Config lives in `.env` (copy from `.env.example`). **The `.env` is loaded from
the current working directory only** (`src/config.py`) — always `cd $CLI_HOME`
before running, or the token silently won't load and requests go out
unauthenticated (the client omits the `Authorization` header instead of
failing).

Required: `COURTLISTENER_API_TOKEN` (legacy alias `COURTLISTENER_API_KEY` also
accepted). Recommended for `dockets download-docs`: `COURTLISTENER_SESSION_ID`
(browser session cookie; expires periodically — see README for how to obtain
it). Other vars: `OUTPUT_FORMAT` (default xlsx), `INCLUDE_TIMESTAMP` (default
true), `COURTLISTENER_DELAY` (default 13.0 s between pages), `LOG_LEVEL`,
`COURTLISTENER_TIMEOUT` (raise to 120 for sorted/heavy queries — the 30 s
default can time out).

Before the first API call of a session, verify the token loads (zero quota
cost, never prints the token):

```bash
cd "$CLI_HOME" && uv run python -c "from src.config import config; t=config.api_token; print('token loaded:', bool(t))"
```

If false, inspect `.env` var names against `.env.example`. To debug a live
request, prefix with `LOG_LEVEL=DEBUG` — e.g.
`LOG_LEVEL=DEBUG uv run courtlistener-cli --screen courts get scotus`.

## Rate limits — plan before querying

Authenticated quota: **5 req/min, 50 req/hour, 125 req/day**. Every page is one
request. Before running anything, estimate pages needed and prefer:

1. `count` sub-commands (opinions/dockets/search/people/courts/audio have one) —
   one request, tells whether a full export is affordable.
2. Tight filters (`--court`, date bounds, `--docket`) over broad crawls.
3. `--limit N` caps rows; `--max-pages N` caps pages; `--limit 0 --max-pages 0`
   is an unbounded crawl — warn the user of the quota cost before running it.

The CLI retries 429s automatically and raises `DailyQuotaExceeded` when the
daily quota is gone. The default 13 s inter-page delay respects the 5/min
limit; lower it via `--delay` only when the user accepts the risk.

## Key semantics

- Pagination: `--limit N` = row cap; `--max-pages N` = page cap; both 0 = crawl
  all. Output includes count, returned_count, pages_fetched, results.
- Batch mode: `dockets list <file.csv|xlsx> --column <name>` queries once per
  row; a column named `id`/`docket_id` fetches by ID directly. Results carry
  `_query_value` tracing the input row. Arbitrary batches: `batch --input-file`
  with `method,endpoint` rows.
- Search `--type`: `o` opinions (default), `d` dockets, `r` filing documents,
  `p` judges, `oa` oral arguments. Search results use camelCase field names
  and a `<mark>`-tagged `snippet`. Details: `docs/SEARCH_TYPES.md`.
- Output: JSON preserves nesting; CSV/XLSX flatten nested dicts to dot-notation
  keys. Files land in the `--output` dir with a `YYYYMMDD_HHMMSS` timestamp
  unless `INCLUDE_TIMESTAMP=false`.
- Financial value codes are ranges (`J` = $1–$15k … `P4` = >$50M), not amounts.
- Citation lookup limits: 250 citations/request, 64k chars, no statutes/id./supra.

## Analyzing results

After any export, profile the file and surface findings relevant to what the
user asked (no pandas in this env — the script is stdlib + openpyxl):

```bash
cd "$CLI_HOME" && uv run python <path-to-this-skill>/scripts/result_stats.py <results-file> [--top N]
```

It prints row/column counts, fill rates, top values for categorical columns
(court, status…), date ranges with per-year counts, and numeric min/max/mean.
Translate its output into insights in the user's terms — e.g. filing volume by
year, dominant courts, gaps in date coverage, duplicate case names, columns
that came back empty (often a sign the filter or search type was wrong). For
deeper one-off questions (top parties, judge overlap, disclosure totals), read
the JSON with a short stdlib Python snippet rather than adding dependencies.

## Tests and development

```bash
make test           # pytest -v --tb=short
make lint           # ruff check --fix + format
uv run python -m pytest tests/test_cli.py::test_name -v   # single test
```

Tests mock HTTP via monkeypatch on `CourtListenerClient.get` — safe to run
without a token or quota. New commands follow the parametrized count-command
pattern in `tests/test_cli.py`.
