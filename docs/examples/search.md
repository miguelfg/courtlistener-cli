# Search Examples

Run a basic search:

```bash
uv run courtlistener-cli search query --q '"qualified immunity"' --type r --limit 20
uv run courtlistener-cli search query --q '"serial number" "firearm"' --type r --limit 100 --max-pages 3
```

Export search results:

```bash
uv run courtlistener-cli search query --q '"habeas corpus"' --type r --format csv --output ./output --filename habeas_results
uv run courtlistener-cli search query --q '"serial number" "firearm"' --type r --format xlsx --output ./output --filename firearm_serials
```

Use pagination and slim exports:

```bash
uv run courtlistener-cli search query --q '"Fourth Amendment"' --type r --limit 100 --max-pages 5 --offset 0
uv run courtlistener-cli search query --q '"Fourth Amendment"' --type r --limit 100 --max-pages 5 --offset 500 --filename fourth_amendment_part_500
uv run courtlistener-cli search query --q '"wire fraud"' --type r --format xlsx --slim --list-sep "|" --filename wire_fraud_slim
```

Advanced search:

```bash
uv run courtlistener-cli search advanced --court scotus --limit 10
uv run courtlistener-cli search advanced --judge "Sotomayor" --date-from 2020-01-01 --date-to 2024-12-31 --format json
uv run courtlistener-cli search advanced --court ca9 --date-from 2023-01-01 --limit 50 --format xlsx
```

Count before exporting:

```bash
uv run courtlistener-cli search count --q '"qualified immunity"' --type r
uv run courtlistener-cli search count --q '"patent infringement"' --type o
```
