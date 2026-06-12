# Search Examples

Run a basic search:

```bash
courtlistener-cli search query --q '"qualified immunity"' --type r --limit 20
courtlistener-cli search query --q '"serial number" "firearm"' --type r --limit 100 --max-pages 3
```

Export search results:

```bash
courtlistener-cli search query --q '"habeas corpus"' --type r --format csv --output ./output --filename habeas_results
courtlistener-cli search query --q '"serial number" "firearm"' --type r --format xlsx --output ./output --filename firearm_serials
```

Use pagination and slim exports:

```bash
courtlistener-cli search query --q '"Fourth Amendment"' --type r --limit 100 --max-pages 5 --offset 0
courtlistener-cli search query --q '"Fourth Amendment"' --type r --limit 100 --max-pages 5 --offset 500 --filename fourth_amendment_part_500
courtlistener-cli search query --q '"wire fraud"' --type r --format xlsx --slim --list-sep "|" --filename wire_fraud_slim
```

Advanced search:

```bash
courtlistener-cli search advanced --court scotus --limit 10
courtlistener-cli search advanced --judge "Sotomayor" --date-from 2020-01-01 --date-to 2024-12-31 --format json
courtlistener-cli search advanced --court ca9 --date-from 2023-01-01 --limit 50 --format xlsx
```

Filter by court:

```bash
# Pass the court_id slug from your exported data (e.g. dcd, ca9, nysd, txnd)
courtlistener-cli search query --q "1:16-cv-00745" --type r --court dcd --format csv
courtlistener-cli search query --q '"serial number" "firearm"' --type d --court ca9 --limit 50 --format xlsx
courtlistener-cli search query --q '"habeas corpus"' --type rd --court nysd --limit 100 --format csv
```

Count before exporting:

```bash
courtlistener-cli search count --q '"qualified immunity"' --type r
courtlistener-cli search count --q '"qualified immunity"' --type r --court ca9
courtlistener-cli search count --q '"patent infringement"' --type o
```
