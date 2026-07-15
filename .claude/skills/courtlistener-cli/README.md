# courtlistener-cli skill

Claude Code skill for running and analyzing [CourtListener API](https://www.courtlistener.com/help/api/rest/) queries through this repo's CLI. Claude picks the right command, plans around rate limits (5 req/min, 125/day), exports JSON/CSV/XLSX, and profiles the results with `scripts/result_stats.py`.

## Example prompts → commands they trigger

### Case law (opinions, clusters)

| Prompt | Command |
|---|---|
| "Get the 20 most recent Supreme Court opinions" | `opinions list --limit 20` |
| "How many opinions mention miranda?" | `opinions count --search "miranda"` |
| "Fetch opinion 106359" | `opinions get 106359` |
| "List SCOTUS opinion clusters filed between 2020 and 2024 as a spreadsheet" | `clusters list --court scotus --date-filed-after 2020-01-01 --date-filed-before 2024-12-31 --format xlsx` |
| "Look up the cluster from this URL: courtlistener.com/opinion/2812209/..." | `clusters get 2812209` |

### Full-text search

| Prompt | Command |
|---|---|
| "Search case law for 'gun control', give me 25 results" | `search query --q '"gun control"' --type o --limit 25` |
| "Find PACER cases involving Apple Inc" | `search query --q "apple inc" --type d` |
| "Search court filings mentioning serial numbers of firearms, export to Excel" | `search query --q '"serial number" firearm' --type r --format xlsx` |
| "Any judges named Ginsburg?" | `search query --q "Ginsburg" --type p` |
| "Find oral arguments about the commerce clause" | `search query --q "commerce clause" --type oa` |
| "How many opinions match 'qualified immunity'?" | `search count --q '"qualified immunity"' --type o` |

### Dockets and PACER data

| Prompt | Command |
|---|---|
| "List 50 dockets from the DC district court" | `dockets list --court dcd --limit 50` |
| "Find docket 1:16-cv-00745 in dcd" | `dockets list --docket-number "1:16-cv-00745" --court dcd` |
| "Look up every docket number in this spreadsheet" | `dockets list data/dockets.xlsx --column docketNumber` |
| "Get all docket entries for case 4214664" | `docket-entries list --docket 4214664 --limit 0 --max-pages 0` |
| "Which PDFs are available for docket entry 123456?" | `recap-documents list --docket-entry 123456 --is-available true` |
| "Who are the parties in docket 4214664?" | `parties list --docket 4214664` |
| "List the attorneys on that case as XLSX" | `attorneys list --docket 4214664 --format xlsx` |
| "Download all documents from docket 4214664" | `dockets download-docs` (needs `COURTLISTENER_SESSION_ID`) |

### Judges and courts

| Prompt | Command |
|---|---|
| "Find judges named Smith" | `people list --name Smith` |
| "Which judges went to law school in Rochester?" | `people list --educations-school-name Rochester` |
| "What positions has judge 1213 held?" | `positions list --person 1213` |
| "Export all federal district courts" | `courts list --jurisdiction FD --limit 0 --max-pages 0` |

### Financial disclosures

| Prompt | Command |
|---|---|
| "Get financial disclosures for judge 1213 as a spreadsheet" | `financial list --person 1213 --format xlsx` |
| "Show investments worth more than $50M" | `financial investments --gross-value-code P4` |
| "Any redacted investment rows?" | `financial investments --redacted true` |
| "What gifts are in disclosure 34187?" | `financial gifts --disclosure 34187` |
| "List that judge's outside board positions" | `financial disclosure-positions --disclosure 34187` |

### Oral arguments, citations, alerts

| Prompt | Command |
|---|---|
| "List recent SCOTUS oral argument recordings" | `audio list --court scotus --limit 20` |
| "Check whether the citations in this paragraph are real" | `citation-lookup text --text "..."` |
| "Verify 576 U.S. 644" | `citation-lookup citation --volume 576 --reporter "U.S." --page 644` |
| "Alert me daily about new Apple filings" | `alerts create --name ... --query 'q=%22Apple%22&type=r' --rate dly --alert-type r` |
| "Notify me of updates on docket 4214664" | `docket-alerts create --docket 4214664` |

### Analysis prompts (after an export)

| Prompt | What happens |
|---|---|
| "Summarize what we just exported" | `scripts/result_stats.py <file>` → row counts, fill rates, top courts, per-year volume |
| "Which court dominates these results?" / "Any gaps in the date coverage?" | stats profile + interpretation |
| "Who are the most frequent parties across these dockets?" | short stdlib Python over the exported JSON |

## Contents

- [`COOKBOOK.md`](COOKBOOK.md) — real `claude -p` sessions with screenshots
- `SKILL.md` — how to run the CLI, rate-limit planning, pagination/batch/search semantics
- `references/commands.md` — auto-generated `--help` dump of all 18 command groups
- `scripts/result_stats.py` — profiles any exported JSON/CSV/XLSX (stdlib + openpyxl)

## Notes

- Every page fetched is one API request against a 125/day quota — Claude runs `count` first and asks before unbounded crawls (`--limit 0 --max-pages 0`).
- Install dir resolved via `$COURTLISTENER_CLI_HOME`, falling back to this repo's root. Nothing gets installed under the skill folder.
