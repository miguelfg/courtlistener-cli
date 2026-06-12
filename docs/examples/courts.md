# Courts Examples

List courts:

```bash
courtlistener-cli courts list --limit 20
courtlistener-cli courts list --limit 100 --max-pages 2 --offset 100 --format csv --output ./output
```

Get a court:

```bash
courtlistener-cli courts get scotus
courtlistener-cli courts get ca9 --format json
```

Search courts:

```bash
courtlistener-cli courts search --jurisdiction F --limit 50
courtlistener-cli courts search --court-type A --format xlsx --output ./output
courtlistener-cli courts search --jurisdiction F --court-type A --limit 100 --max-pages 2
```

Count courts:

```bash
courtlistener-cli courts count
courtlistener-cli courts count --jurisdiction F
courtlistener-cli courts count --jurisdiction F --court-type A
```
