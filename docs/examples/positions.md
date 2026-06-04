# Positions Examples

List positions:

```bash
uv run courtlistener-cli positions list --limit 20
uv run courtlistener-cli positions list --person 1234 --limit 50
uv run courtlistener-cli positions list --court scotus --order-by date_start --format xlsx --output ./output
uv run courtlistener-cli positions list --person 1234 --court scotus --format json
```

Get one position:

```bash
uv run courtlistener-cli positions get 98765
```
