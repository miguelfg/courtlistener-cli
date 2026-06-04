# Dockets Examples

List dockets:

```bash
uv run courtlistener-cli dockets list --limit 20
uv run courtlistener-cli dockets list --court cand --case-name "United States" --limit 50 --format csv --output ./output
uv run courtlistener-cli dockets list data/dockets.xlsx --column docketNumber --limit 50 --max-pages 5 --format json
```

Get a docket:

```bash
uv run courtlistener-cli dockets get 4134326
uv run courtlistener-cli dockets get 4134326 --format json
```

List docket entries:

```bash
uv run courtlistener-cli dockets entries 4134326 --limit 50
uv run courtlistener-cli dockets entries 4134326 --limit 200 --max-pages 3 --format xlsx --output ./output --filename docket_4134326_entries
uv run courtlistener-cli dockets entries 4134326 --format csv --slim --filename docket_4134326_entries_slim
```

Count dockets:

```bash
uv run courtlistener-cli dockets count
uv run courtlistener-cli dockets count --court cand
uv run courtlistener-cli dockets count --court cand --case-name "United States"
```

Download docket documents:

```bash
uv run courtlistener-cli dockets download-docs 4134326 --output ./output
uv run courtlistener-cli dockets download-docs 4134326 --output ./output --manifest csv
uv run courtlistener-cli dockets download-docs 4134326 --output ./output --manifest xlsx --all-docs
```

Export docket parties:

```bash
uv run courtlistener-cli dockets parties 4134326
uv run courtlistener-cli dockets parties 4134326 --format json --output ./output
uv run courtlistener-cli dockets parties 4134326 --format xlsx --output ./output --filename docket_4134326_parties
```
