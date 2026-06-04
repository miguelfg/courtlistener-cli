# Courts Examples

List courts:

```bash
uv run courtlistener-cli courts list --limit 20
uv run courtlistener-cli courts list --limit 100 --max-pages 2 --offset 100 --format csv --output ./output
```

Get a court:

```bash
uv run courtlistener-cli courts get scotus
uv run courtlistener-cli courts get ca9 --format json
```

Search courts:

```bash
uv run courtlistener-cli courts search --jurisdiction F --limit 50
uv run courtlistener-cli courts search --court-type A --format xlsx --output ./output
uv run courtlistener-cli courts search --jurisdiction F --court-type A --limit 100 --max-pages 2
```

Count courts:

```bash
uv run courtlistener-cli courts count
uv run courtlistener-cli courts count --jurisdiction F
uv run courtlistener-cli courts count --jurisdiction F --court-type A
```
