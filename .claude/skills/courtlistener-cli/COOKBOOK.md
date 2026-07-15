# Cookbook — courtlistener-cli skill

Real sessions run with `claude -p "<prompt>"` from the repo root. Each recipe shows the prompt, what the skill does under the hood, and the result. Every recipe costs real API quota (5 req/min, 125/day) — the skill runs `count` first when a query could fan out.

## 1. Recent SCOTUS oral arguments

```bash
claude -p "List recent SCOTUS oral argument recordings"
```

Skill runs `audio list --court scotus --limit 20`, saves JSON, and answers with a table of argued date, case name, and duration — flagging cost (1 API request) and offering follow-ups:

![Claude listing 20 recent SCOTUS oral arguments with dates and durations](assets/demo-audio-list.png)

## 2. Count before you crawl

```bash
claude -p "How many opinions match 'qualified immunity'? If it's under 200, export them all to xlsx"
```

Skill runs `search count --q '"qualified immunity"' --type o` first (1 request). Only if the count is affordable does it launch `search query ... --format xlsx`, estimating pages against the daily quota before starting.

<!-- TODO screenshot: count answer + go/no-go decision -->

## 3. Docket deep dive

```bash
claude -p "Who are the parties and attorneys in docket 4214664, and what are its latest entries?"
```

Three commands, one docket:

```
parties list --docket 4214664
attorneys list --docket 4214664
docket-entries list --docket 4214664 --limit 25
```

Answer merges them: party roles, counsel per party, most recent filings.

<!-- TODO screenshot: merged parties/attorneys/entries answer -->

## 4. Batch lookup from a spreadsheet

```bash
claude -p "Look up every docket number in data/dockets.xlsx in the dcd court and export to xlsx"
```

Skill runs `dockets list data/dockets.xlsx --column docketNumber --court dcd --format xlsx`. One paginated query per row; results carry `_query_value` tracing which input row matched. Skill warns first when the sheet has many rows (each row ≥ 1 request).

<!-- TODO screenshot: batch run with per-row progress lines -->

## 5. Citation hallucination check

```bash
claude -p "Check whether the citations in this text are real: Obergefell v. Hodges (576 U.S. 644) established the right to marriage, following Roe v. Wade (410 U.S. 113)."
```

Skill runs `citation-lookup text --text "..."` and reports per citation: found (200), not found (404 — possible hallucination), ambiguous (300), with the matched clusters.

<!-- TODO screenshot: verdict list with statuses -->

## 6. Profile an export

```bash
claude -p "Summarize the latest results file in ./output — top courts, per-year volume, empty columns"
```

No API request. Skill runs `scripts/result_stats.py <file>` and interprets: dominant courts, filing volume per year, date-coverage gaps, columns that came back empty (usually a wrong filter or search type).

<!-- TODO screenshot: stats profile + interpretation -->

## Screenshots still to capture

Run the recipe's `claude -p` command, screenshot the terminal answer, drop the PNG in `assets/`, replace the TODO comment with `![alt](assets/<name>.png)`.

| Recipe | Suggested filename |
|---|---|
| 2 — count-first decision | `demo-count-first.png` |
| 3 — docket deep dive | `demo-docket-deep-dive.png` |
| 4 — batch spreadsheet lookup | `demo-batch-lookup.png` |
| 5 — citation check | `demo-citation-check.png` |
| 6 — stats profile | `demo-result-stats.png` |
