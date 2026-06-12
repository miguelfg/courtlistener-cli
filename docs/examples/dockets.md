# Dockets Examples

List dockets:

```bash
courtlistener-cli dockets list --limit 20
courtlistener-cli dockets list --court cand --case-name "United States" --limit 50 --format csv --output ./output
courtlistener-cli dockets list data/dockets.xlsx --column docketNumber --limit 50 --max-pages 5 --format json
```

Get a docket:

```bash
courtlistener-cli dockets get 4134326
courtlistener-cli dockets get 4134326 --format json
```

List docket entries:

```bash
courtlistener-cli dockets entries 4134326 --limit 50
courtlistener-cli dockets entries 4134326 --limit 200 --max-pages 3 --format xlsx --output ./output --filename docket_4134326_entries
courtlistener-cli dockets entries 4134326 --format csv --slim --filename docket_4134326_entries_slim
```

Count dockets:

```bash
courtlistener-cli dockets count
courtlistener-cli dockets count --court cand
courtlistener-cli dockets count --court cand --case-name "United States"
```

Download docket documents:

```bash
courtlistener-cli dockets download-docs 4134326 --output ./output
courtlistener-cli dockets download-docs 4134326 --output ./output --manifest csv
courtlistener-cli dockets download-docs 4134326 --output ./output --manifest xlsx --all-docs
```

Export docket parties:

```bash
courtlistener-cli dockets parties 4134326
courtlistener-cli dockets parties 4134326 --format json --output ./output
courtlistener-cli dockets parties 4134326 --format xlsx --output ./output --filename docket_4134326_parties
```
