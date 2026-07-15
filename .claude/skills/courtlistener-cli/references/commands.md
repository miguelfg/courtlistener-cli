# courtlistener-cli command reference (auto-generated)

Generated from live `--help` output via `click.testing.CliRunner` walking `src.cli:main` recursively. Regenerate after CLI changes by re-running that dump (see skill git history) or spot-check with `uv run courtlistener-cli <group> <cmd> --help`.

## `courtlistener-cli`

```text
Usage: main [OPTIONS] COMMAND [ARGS]...

  CourtListener REST API Python CLI Client

  Access federal and state case law, PACER data, RECAP Archive, oral arguments,
  judge information, and financial disclosures.

Options:
  --version      Show the version and exit.
  --no-cache     Disable local caching for this request
  --screen       Print results to screen (JSON format)
  --delay FLOAT  Delay between paginated requests (seconds)
  --help         Show this message and exit.

Commands:
  alerts           Manage search alerts (email/webhook when new matching...
  attorneys        Manage PACER case attorneys
  audio            Manage oral argument recordings
  batch            Process batch requests from files
  citation-lookup  Look up and verify legal citations (useful for detecting...
  clusters         Manage opinion clusters (groups of decisions for a...
  courts           Manage court information
  docket-alerts    Manage docket alerts (notifications when a specific case...
  docket-entries   Manage PACER docket entries (rows on a docket)
  dockets          Manage case dockets
  financial        Financial disclosure records for federal judges (Ethics...
  opinions         Manage opinions (court decisions)
  parties          Manage PACER case parties (plaintiffs, defendants, etc.)
  people           Manage judge and attorney information
  positions        Manage judicial positions held by people (judges,...
  recap-documents  Manage RECAP Archive documents (PDFs from PACER)
  search           Search across all legal data
  tags             Manage user-created tags linked to dockets
```

## `courtlistener-cli alerts`

```text
Usage: main alerts [OPTIONS] COMMAND [ARGS]...

  Manage search alerts (email/webhook when new matching results appear)

Options:
  --help  Show this message and exit.

Commands:
  create  Create a new search alert
  delete  Delete a search alert
  list    List your search alerts
  update  Update an existing search alert (PATCH)
```

## `courtlistener-cli alerts create`

```text
Usage: main alerts create [OPTIONS]

  Create a new search alert

Options:
  --name TEXT              Human-friendly name for the alert  [required]
  --query TEXT             URL-encoded query string from CourtListener front end
                           (e.g. q=foo&type=o)  [required]
  --rate [rt|dly|wly|mly]  Email frequency: rt=real-time, dly=daily, wly=weekly,
                           mly=monthly  [required]
  --alert-type TEXT        For RECAP: d (dockets only) or r (dockets + filings)
  --help                   Show this message and exit.
```

## `courtlistener-cli alerts delete`

```text
Usage: main alerts delete [OPTIONS]

  Delete a search alert

Options:
  --id INTEGER  Alert ID to delete  [required]
  --confirm     Confirm deletion (required)  [required]
  --help        Show this message and exit.
```

## `courtlistener-cli alerts list`

```text
Usage: main alerts list [OPTIONS]

  List your search alerts

Options:
  --limit INTEGER           Total results to export; 0 with --max-pages 0 = all
                            results
  --max-pages INTEGER
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli alerts update`

```text
Usage: main alerts update [OPTIONS]

  Update an existing search alert (PATCH)

Options:
  --id INTEGER             Alert ID to update  [required]
  --name TEXT              New name
  --query TEXT             New query string
  --rate [rt|dly|wly|mly]  New email frequency
  --help                   Show this message and exit.
```

## `courtlistener-cli attorneys`

```text
Usage: main attorneys [OPTIONS] COMMAND [ARGS]...

  Manage PACER case attorneys

Options:
  --help  Show this message and exit.

Commands:
  get   Get a specific attorney by ID
  list  List attorneys in PACER cases.
```

## `courtlistener-cli attorneys get`

```text
Usage: main attorneys get [OPTIONS] ATTORNEY_ID

  Get a specific attorney by ID

Options:
  --help  Show this message and exit.
```

## `courtlistener-cli attorneys list`

```text
Usage: main attorneys list [OPTIONS]

  List attorneys in PACER cases.

  Note: nested parties_represented is NOT filtered to the docket by default. Use
  --filter-nested-results to scope nested records to the specified docket.

Options:
  --docket INTEGER          Filter to attorneys for a specific docket ID
  --filter-nested-results   Filter nested party data to match the docket filter
  --limit INTEGER           Total results to export; 0 with --max-pages 0 = all
                            results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli audio`

```text
Usage: main audio [OPTIONS] COMMAND [ARGS]...

  Manage oral argument recordings

Options:
  --help  Show this message and exit.

Commands:
  count  Return total matching recordings count
  get    Get audio details by ID
  list   List oral argument recordings
```

## `courtlistener-cli audio count`

```text
Usage: main audio count [OPTIONS]

  Return total matching recordings count

Options:
  --court TEXT    Filter by court
  --year INTEGER  Filter by year
  --help          Show this message and exit.
```

## `courtlistener-cli audio get`

```text
Usage: main audio get [OPTIONS] AUDIO_ID

  Get audio details by ID

Options:
  --help  Show this message and exit.
```

## `courtlistener-cli audio list`

```text
Usage: main audio list [OPTIONS]

  List oral argument recordings

Options:
  --limit INTEGER           Total results to export; use 0 with --max-pages 0 to
                            export all results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --offset INTEGER          Pagination offset
  --court TEXT              Filter by court
  --year INTEGER            Filter by year
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli batch`

```text
Usage: main batch [OPTIONS] COMMAND [ARGS]...

  Process batch requests from files

Options:
  --help  Show this message and exit.

Commands:
  process  Process batch requests from CSV or JSON Lines file CSV Format:...
```

## `courtlistener-cli batch process`

```text
Usage: main batch process [OPTIONS]

  Process batch requests from CSV or JSON Lines file

  CSV Format: method,endpoint,param1,param2 JSON Lines: One JSON object per line

Options:
  --input-file PATH         Input CSV or JSON Lines file  [required]
  --format [json|csv|xlsx]  Output format
  --output PATH             Output directory
  --limit INTEGER           Process only first N requests
  --verbose                 Show details for each request
  --help                    Show this message and exit.
```

## `courtlistener-cli citation-lookup`

```text
Usage: main citation-lookup [OPTIONS] COMMAND [ARGS]...

  Look up and verify legal citations (useful for detecting AI hallucinations)

Options:
  --help  Show this message and exit.

Commands:
  citation  Look up a single citation by volume, reporter, and page.
  text      Find and verify all citations in a block of text.
```

## `courtlistener-cli citation-lookup citation`

```text
Usage: main citation-lookup citation [OPTIONS]

  Look up a single citation by volume, reporter, and page.

Options:
  --volume INTEGER  Volume number  [required]
  --reporter TEXT   Reporter abbreviation (e.g. "U.S.")  [required]
  --page TEXT       Page number  [required]
  --output PATH
  --help            Show this message and exit.
```

## `courtlistener-cli citation-lookup text`

```text
Usage: main citation-lookup text [OPTIONS]

  Find and verify all citations in a block of text.

  Limits: 250 citations per request, 60 valid citations/minute, 64,000 chars
  max. Does not look up statutes, id., or supra citations.

Options:
  --text TEXT      Blob of text to scan for citations (max 64,000 characters)
                   [required]
  --format [json]
  --output PATH
  --help           Show this message and exit.
```

## `courtlistener-cli clusters`

```text
Usage: main clusters [OPTIONS] COMMAND [ARGS]...

  Manage opinion clusters (groups of decisions for a single case)

Options:
  --help  Show this message and exit.

Commands:
  count  Return total matching clusters count
  get    Get a specific opinion cluster by ID
  list   List opinion clusters with pagination
```

## `courtlistener-cli clusters count`

```text
Usage: main clusters count [OPTIONS]

  Return total matching clusters count

Options:
  --docket INTEGER  Filter by docket ID
  --court TEXT      Filter by court ID (docket__court)
  --help            Show this message and exit.
```

## `courtlistener-cli clusters get`

```text
Usage: main clusters get [OPTIONS] CLUSTER_ID

  Get a specific opinion cluster by ID

Options:
  --format [json|csv|xlsx]
  --help                    Show this message and exit.
```

## `courtlistener-cli clusters list`

```text
Usage: main clusters list [OPTIONS]

  List opinion clusters with pagination

Options:
  --limit INTEGER           Total results to export; 0 with --max-pages 0 = all
                            results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --docket INTEGER          Filter by docket ID
  --docket-number TEXT      Filter by docket number (docket__docket_number)
  --court TEXT              Filter by court ID via join (docket__court)
  --date-filed-after TEXT   Filed on or after ISO-8601 date
  --date-filed-before TEXT  Filed on or before ISO-8601 date
  --order-by TEXT           Sort field, prefix - for descending
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli courts`

```text
Usage: main courts [OPTIONS] COMMAND [ARGS]...

  Manage court information

Options:
  --help  Show this message and exit.

Commands:
  count   Return total matching courts count
  get     Get court details by ID
  list    List all courts
  search  Search courts by jurisdiction or type
```

## `courtlistener-cli courts count`

```text
Usage: main courts count [OPTIONS]

  Return total matching courts count

Options:
  --jurisdiction TEXT  Filter by jurisdiction
  --court-type TEXT    Filter by court type (federal/state)
  --help               Show this message and exit.
```

## `courtlistener-cli courts get`

```text
Usage: main courts get [OPTIONS] COURT_ID

  Get court details by ID

Options:
  --format [json]
  --help           Show this message and exit.
```

## `courtlistener-cli courts list`

```text
Usage: main courts list [OPTIONS]

  List all courts

Options:
  --limit INTEGER           Total results to export; use 0 with --max-pages 0 to
                            export all results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --offset INTEGER          Pagination offset
  --delay FLOAT             Delay between requests in seconds
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli courts search`

```text
Usage: main courts search [OPTIONS]

  Search courts by jurisdiction or type

Options:
  --jurisdiction TEXT       Filter by jurisdiction
  --court-type TEXT         Filter by court type (federal/state)
  --limit INTEGER           Total results to export; use 0 with --max-pages 0 to
                            export all results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --offset INTEGER          Pagination offset
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli docket-alerts`

```text
Usage: main docket-alerts [OPTIONS] COMMAND [ARGS]...

  Manage docket alerts (notifications when a specific case is updated)

Options:
  --help  Show this message and exit.

Commands:
  create  Subscribe to updates for a specific docket
  delete  Unsubscribe from a docket alert
  list    List your docket alerts
```

## `courtlistener-cli docket-alerts create`

```text
Usage: main docket-alerts create [OPTIONS]

  Subscribe to updates for a specific docket

Options:
  --docket INTEGER      Docket ID to subscribe to  [required]
  --alert-type INTEGER  1=subscribe (default), 0=unsubscribe (@recap.email auto-
                        subscribe only)
  --help                Show this message and exit.
```

## `courtlistener-cli docket-alerts delete`

```text
Usage: main docket-alerts delete [OPTIONS]

  Unsubscribe from a docket alert

Options:
  --id INTEGER  Docket alert ID to delete  [required]
  --confirm     Confirm deletion (required)  [required]
  --help        Show this message and exit.
```

## `courtlistener-cli docket-alerts list`

```text
Usage: main docket-alerts list [OPTIONS]

  List your docket alerts

Options:
  --limit INTEGER
  --max-pages INTEGER
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli docket-entries`

```text
Usage: main docket-entries [OPTIONS] COMMAND [ARGS]...

  Manage PACER docket entries (rows on a docket)

Options:
  --help  Show this message and exit.

Commands:
  get   Get a specific docket entry by ID
  list  List docket entries for a PACER docket
```

## `courtlistener-cli docket-entries get`

```text
Usage: main docket-entries get [OPTIONS] ENTRY_ID

  Get a specific docket entry by ID

Options:
  --help  Show this message and exit.
```

## `courtlistener-cli docket-entries list`

```text
Usage: main docket-entries list [OPTIONS]

  List docket entries for a PACER docket

Options:
  --docket INTEGER          Filter to entries for a specific docket ID
                            [required]
  --limit INTEGER           Total results to export; 0 with --max-pages 0 = all
                            results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --order-by TEXT           Sort field, prefix - for descending
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli dockets`

```text
Usage: main dockets [OPTIONS] COMMAND [ARGS]...

  Manage case dockets

Options:
  --help  Show this message and exit.

Commands:
  count          Return total matching dockets count
  download-docs  Download all free PDFs for a docket and generate a manifest.
  entries        Get entries for a specific docket
  get            Get docket details by ID
  list           List case dockets or batch query from input CSV/XLSX.
  parties        Get parties and criminal charges for a docket.
```

## `courtlistener-cli dockets count`

```text
Usage: main dockets count [OPTIONS]

  Return total matching dockets count

Options:
  --court TEXT      Filter by court ID
  --case-name TEXT  Filter by case name
  --help            Show this message and exit.
```

## `courtlistener-cli dockets download-docs`

```text
Usage: main dockets download-docs [OPTIONS] DOCKET_ID

  Download all free PDFs for a docket and generate a manifest.

  By default only fetches available docs (is_available=True), which is fast and
  avoids rate-limit throttling. Use --all-docs to include unavailable ones.

Options:
  --output PATH                   Parent directory for downloaded files
  --manifest [xlsx|csv]           Format for the manifest spreadsheet
  --all-docs                      Also fetch unavailable docs (slower —
                                  paginates all recap documents)
  --folder-name-mode [case-name-number|case-name|docket-number|docket-id|none]
                                  Choose how the download folder is named; use
                                  none to write directly into --output
  --help                          Show this message and exit.
```

## `courtlistener-cli dockets entries`

```text
Usage: main dockets entries [OPTIONS] DOCKET_ID

  Get entries for a specific docket

Options:
  --limit INTEGER           Total results to export; use 0 with --max-pages 0 to
                            export all results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --format [json|csv|xlsx]
  --output PATH
  --filename TEXT           Output filename stem (without extension)
  --slim                    Also export a slim version with key fields only
  --help                    Show this message and exit.
```

## `courtlistener-cli dockets get`

```text
Usage: main dockets get [OPTIONS] DOCKET_ID

  Get docket details by ID

Options:
  --format [json]
  --help           Show this message and exit.
```

## `courtlistener-cli dockets list`

```text
Usage: main dockets list [OPTIONS] [INPUT_FILE]

  List case dockets or batch query from input CSV/XLSX.

Options:
  --column TEXT             Column name in input CSV/XLSX containing docket
                            numbers or IDs
  --limit INTEGER           Total results to export per request; use 0 with
                            --max-pages 0 to export all results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --offset INTEGER          Pagination offset
  --court TEXT              Filter by court ID
  --docket-number TEXT      Filter by docket number
  --case-name TEXT          Filter by case name
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli dockets parties`

```text
Usage: main dockets parties [OPTIONS] DOCKET_ID

  Get parties and criminal charges for a docket.

  Fetches all parties (defendants, attorneys, etc.) for DOCKET_ID and includes
  their criminal counts (charge description, disposition) when present — i.e.
  the charges/citations table from the Parties & Attorneys tab.

Options:
  --format [json|csv|xlsx]
  --output PATH
  --filename TEXT           Output filename stem (without extension); defaults
                            to parties_{docket_id}
  --help                    Show this message and exit.
```

## `courtlistener-cli financial`

```text
Usage: main financial [OPTIONS] COMMAND [ARGS]...

  Financial disclosure records for federal judges (Ethics in Government Act)

Options:
  --help  Show this message and exit.

Commands:
  agreements              List agreements or arrangements reported in...
  debts                   List liabilities reported in financial disclosures
  disclosure-positions    List outside positions held (officer, director,...
  get                     Get a specific financial disclosure by ID
  gifts                   List gifts received by judges in financial...
  investments             List investment income holdings for financial...
  list                    List financial disclosure records
  non-investment-incomes  List non-investment earned income (≥$200) in...
```

## `courtlistener-cli financial agreements`

```text
Usage: main financial agreements [OPTIONS]

  List agreements or arrangements reported in financial disclosures

Options:
  --disclosure INTEGER      Filter by financial disclosure ID
  --limit INTEGER
  --max-pages INTEGER
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli financial debts`

```text
Usage: main financial debts [OPTIONS]

  List liabilities reported in financial disclosures

Options:
  --disclosure INTEGER      Filter by financial disclosure ID
  --redacted BOOLEAN        Filter to rows with redacted data
  --limit INTEGER
  --max-pages INTEGER
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli financial disclosure-positions`

```text
Usage: main financial disclosure-positions [OPTIONS]

  List outside positions held (officer, director, trustee) from financial
  disclosures

Options:
  --disclosure INTEGER      Filter by financial disclosure ID
  --limit INTEGER
  --max-pages INTEGER
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli financial get`

```text
Usage: main financial get [OPTIONS] DISCLOSURE_ID

  Get a specific financial disclosure by ID

Options:
  --help  Show this message and exit.
```

## `courtlistener-cli financial gifts`

```text
Usage: main financial gifts [OPTIONS]

  List gifts received by judges in financial disclosures

Options:
  --disclosure INTEGER      Filter by financial disclosure ID
  --redacted BOOLEAN        Filter to rows with redacted data
  --limit INTEGER
  --max-pages INTEGER
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli financial investments`

```text
Usage: main financial investments [OPTIONS]

  List investment income holdings for financial disclosures

Options:
  --disclosure INTEGER      Filter by financial disclosure ID
  --redacted BOOLEAN        Filter to rows with redacted data (True/False)
  --gross-value-code TEXT   Filter by gross value code (e.g. P4 for >$50M)
  --limit INTEGER
  --max-pages INTEGER
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli financial list`

```text
Usage: main financial list [OPTIONS]

  List financial disclosure records

Options:
  --person INTEGER          Filter by judge person ID
  --year INTEGER            Filter by disclosure year
  --limit INTEGER
  --max-pages INTEGER
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli financial non-investment-incomes`

```text
Usage: main financial non-investment-incomes [OPTIONS]

  List non-investment earned income (≥$200) in financial disclosures

Options:
  --disclosure INTEGER      Filter by financial disclosure ID
  --limit INTEGER
  --max-pages INTEGER
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli opinions`

```text
Usage: main opinions [OPTIONS] COMMAND [ARGS]...

  Manage opinions (court decisions)

Options:
  --help  Show this message and exit.

Commands:
  count  Return total matching opinions count
  get    Get a specific opinion
  list   List opinions with pagination
```

## `courtlistener-cli opinions count`

```text
Usage: main opinions count [OPTIONS]

  Return total matching opinions count

Options:
  --search TEXT  Full-text search
  --help         Show this message and exit.
```

## `courtlistener-cli opinions get`

```text
Usage: main opinions get [OPTIONS] OPINION_ID

  Get a specific opinion

Options:
  --format [json|csv|xlsx]
  --help                    Show this message and exit.
```

## `courtlistener-cli opinions list`

```text
Usage: main opinions list [OPTIONS]

  List opinions with pagination

Options:
  --limit INTEGER           Total results to export; use 0 with --max-pages 0 to
                            export all results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --offset INTEGER          Pagination offset
  --search TEXT             Full-text search
  --format [json|csv|xlsx]  Output format
  --output PATH             Output directory
  --help                    Show this message and exit.
```

## `courtlistener-cli parties`

```text
Usage: main parties [OPTIONS] COMMAND [ARGS]...

  Manage PACER case parties (plaintiffs, defendants, etc.)

Options:
  --help  Show this message and exit.

Commands:
  list  List parties in PACER cases.
```

## `courtlistener-cli parties list`

```text
Usage: main parties list [OPTIONS]

  List parties in PACER cases.

  Note: nested attorney data is NOT filtered to the docket by default. Use
  --filter-nested-results to scope nested records to the specified docket.

Options:
  --docket INTEGER          Filter to parties for a specific docket ID
  --filter-nested-results   Filter nested attorney data to match the docket
                            filter
  --limit INTEGER           Total results to export; 0 with --max-pages 0 = all
                            results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli people`

```text
Usage: main people [OPTIONS] COMMAND [ARGS]...

  Manage judge and attorney information

Options:
  --help  Show this message and exit.

Commands:
  count  Return total matching people count
  get    Get person details by ID
  list   List judges and attorneys
```

## `courtlistener-cli people count`

```text
Usage: main people count [OPTIONS]

  Return total matching people count

Options:
  --name TEXT  Filter by person name
  --help       Show this message and exit.
```

## `courtlistener-cli people get`

```text
Usage: main people get [OPTIONS] PERSON_ID

  Get person details by ID

Options:
  --help  Show this message and exit.
```

## `courtlistener-cli people list`

```text
Usage: main people list [OPTIONS]

  List judges and attorneys

Options:
  --limit INTEGER           Total results to export; use 0 with --max-pages 0 to
                            export all results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --offset INTEGER          Pagination offset
  --name TEXT               Filter by person name
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli positions`

```text
Usage: main positions [OPTIONS] COMMAND [ARGS]...

  Manage judicial positions held by people (judges, appointers, etc.)

Options:
  --help  Show this message and exit.

Commands:
  get   Get a specific position by ID
  list  List judicial positions held by people
```

## `courtlistener-cli positions get`

```text
Usage: main positions get [OPTIONS] POSITION_ID

  Get a specific position by ID

Options:
  --help  Show this message and exit.
```

## `courtlistener-cli positions list`

```text
Usage: main positions list [OPTIONS]

  List judicial positions held by people

Options:
  --person INTEGER          Filter to positions for a specific person ID
  --court TEXT              Filter by court ID
  --limit INTEGER           Total results to export; 0 with --max-pages 0 = all
                            results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --order-by TEXT           Sort field, prefix - for descending
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli recap-documents`

```text
Usage: main recap-documents [OPTIONS] COMMAND [ARGS]...

  Manage RECAP Archive documents (PDFs from PACER)

Options:
  --help  Show this message and exit.

Commands:
  get    Get a specific RECAP document by ID
  list   List RECAP documents.
  query  Fast lookup: check if PACER documents are available in RECAP Archive.
```

## `courtlistener-cli recap-documents get`

```text
Usage: main recap-documents get [OPTIONS] DOCUMENT_ID

  Get a specific RECAP document by ID

Options:
  --help  Show this message and exit.
```

## `courtlistener-cli recap-documents list`

```text
Usage: main recap-documents list [OPTIONS]

  List RECAP documents. Omit plain_text for faster responses.

Options:
  --docket-entry INTEGER    Filter by docket entry ID
  --is-available BOOLEAN    Filter to documents available in RECAP (True/False)
  --limit INTEGER           Total results to export; 0 with --max-pages 0 = all
                            results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --order-by TEXT           Sort field, prefix - for descending
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli recap-documents query`

```text
Usage: main recap-documents query [OPTIONS]

  Fast lookup: check if PACER documents are available in RECAP Archive.

  Note: This endpoint is only available to select users.

Options:
  --court TEXT              Court ID (matches PACER subdomain)  [required]
  --pacer-doc-id TEXT       Comma-separated PACER document IDs (up to 300); 4th
                            digit normalized to 0  [required]
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

## `courtlistener-cli search`

```text
Usage: main search [OPTIONS] COMMAND [ARGS]...

  Search across all legal data

Options:
  --help  Show this message and exit.

Commands:
  advanced  Advanced search with filters
  count     Return total matching search results count
  query     Search for opinions, dockets, and other data
```

## `courtlistener-cli search advanced`

```text
Usage: main search advanced [OPTIONS]

  Advanced search with filters

Options:
  --court TEXT              Filter by court
  --judge TEXT              Filter by judge
  --date-from TEXT          Start date (YYYY-MM-DD)
  --date-to TEXT            End date (YYYY-MM-DD)
  --limit INTEGER           Results per page
  --format [json|csv|xlsx]
  --help                    Show this message and exit.
```

## `courtlistener-cli search count`

```text
Usage: main search count [OPTIONS]

  Return total matching search results count

Options:
  --q TEXT      Search query  [required]
  --type TEXT   Type code (default: r).
  --court TEXT  Filter by court ID (e.g. dcd, ca9). Matches court_id field in
                results.
  --help        Show this message and exit.
```

## `courtlistener-cli search query`

```text
Usage: main search query [OPTIONS]

  Search for opinions, dockets, and other data

Options:
  --q TEXT                  Search query  [required]
  --type TEXT               Type code (default: r).
  --court TEXT              Filter by court ID (e.g. dcd, ca9). Matches court_id
                            field in results.
  --limit INTEGER           Total results to export; use 0 with --max-pages 0 to
                            export all results
  --max-pages INTEGER       Maximum pages to fetch (0 = no page cap)
  --offset INTEGER          Pagination offset
  --format [json|csv|xlsx]
  --output PATH
  --slim                    Also export a slim version with key fields only
  --filename TEXT           Output filename stem (without extension)
  --list-sep TEXT           Separator for list fields in CSV/XLSX (empty string
                            or "none" to keep as JSON)
  --help                    Show this message and exit.
```

## `courtlistener-cli tags`

```text
Usage: main tags [OPTIONS] COMMAND [ARGS]...

  Manage user-created tags linked to dockets

Options:
  --help  Show this message and exit.

Commands:
  get   Get a specific tag by ID
  list  List user-created tags
```

## `courtlistener-cli tags get`

```text
Usage: main tags get [OPTIONS] TAG_ID

  Get a specific tag by ID

Options:
  --help  Show this message and exit.
```

## `courtlistener-cli tags list`

```text
Usage: main tags list [OPTIONS]

  List user-created tags

Options:
  --limit INTEGER           Total results to export; 0 with --max-pages 0 = all
                            results
  --max-pages INTEGER
  --format [json|csv|xlsx]
  --output PATH
  --help                    Show this message and exit.
```

