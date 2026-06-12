# Batch Examples

Process a CSV batch file:

```bash
courtlistener-cli batch process --input-file data/sample-batch.csv --format json
courtlistener-cli batch process --input-file data/sample-batch.csv --format csv --output ./output
courtlistener-cli batch process --input-file data/sample-batch.csv --format xlsx --output ./output --limit 25 --verbose
```

Example `data/sample-batch.csv`:

```csv
method,endpoint,limit
GET,/opinions/,20
GET,/courts/,50
GET,/search/,10
```
