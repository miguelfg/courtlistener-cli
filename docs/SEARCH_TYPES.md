# Search Type Guide (`d`, `r`, `rd`)

CourtListener search supports multiple result modes via `--type`.  
Use this guide to pick the right mode for `search query` and `search count`.

## Quick Comparison

### `--type d` (dockets only)
- Returns one result per docket (case-level results).
- No filing-document preview objects are included in each result.
- Best when you want a clean list of cases.

### `--type r` (dockets + up to 3 matching filings)
- Returns one result per docket.
- Includes up to 3 matching filing documents nested in each docket result.
- Can include a flag like `more_docs=true` when more matching filings exist.
- Best when you want case-level results plus a quick filing preview.

### `--type rd` (filing documents only)
- Returns filing documents as a flat list (document-level results).
- Best when you want to export/analyze each matching filing directly.
- You can use returned docket identifiers to link documents back to dockets.

## Which one should I use?

- Use `d` for case lists.
- Use `r` for case lists with filing previews.
- Use `rd` for filing-by-filing analysis.

## CLI Examples

### Case-level search (dockets only)
```bash
uv run courtlistener-cli search query \
  --q '"serial number" "firearm"' \
  --type d \
  --limit 25 \
  --format json
```

### Case-level search with filing previews
```bash
uv run courtlistener-cli search query \
  --q '"serial number" "firearm"' \
  --type r \
  --limit 25 \
  --format json
```

### Filing-level search
```bash
uv run courtlistener-cli search query \
  --q '"serial number" "firearm"' \
  --type rd \
  --limit 100 \
  --format xlsx
```

### Count examples
```bash
# Count matching dockets only
uv run courtlistener-cli search count --q '"serial number" "firearm"' --type d

# Count matching dockets (with filing preview mode)
uv run courtlistener-cli search count --q '"serial number" "firearm"' --type r

# Count matching filing documents
uv run courtlistener-cli search count --q '"serial number" "firearm"' --type rd
```

## Notes

- For large result sets, API counts in some modes may be approximate.
- If you need exact exports, rely on paginated retrieval (`search query`) and materialized output files.
