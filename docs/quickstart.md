# Quickstart

Check the top-level help:

```bash
uv run courtlistener-cli --help
```

List recent opinions:

```bash
uv run courtlistener-cli opinions list --limit 10 --format json
```

Search opinions:

```bash
uv run courtlistener-cli search query --q '"serial number" "firearm"' --type r --limit 25
```

Export search results to XLSX:

```bash
uv run courtlistener-cli search query --q '"serial number" "firearm"' --limit 100 --format xlsx --output ./output --filename firearm_serials
```

Fetch a docket and its entries:

```bash
uv run courtlistener-cli dockets get 4134326
uv run courtlistener-cli dockets entries 4134326 --limit 100 --format xlsx --output ./output --filename docket_4134326_entries
```

Count before exporting a large result set:

```bash
uv run courtlistener-cli search count --q '"habeas corpus"' --type r
```

Filter search results to a specific court:

```bash
# Use the court_id slug from your exported data (e.g. dcd, ca9, nysd)
uv run courtlistener-cli search query --q "1:16-cv-00745" --type r --court dcd --format csv
uv run courtlistener-cli search count --q '"habeas corpus"' --type r --court ca9
```
