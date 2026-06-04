# Audio Examples

List oral arguments:

```bash
uv run courtlistener-cli audio list --limit 20
uv run courtlistener-cli audio list --court scotus --limit 50
uv run courtlistener-cli audio list --court ca9 --year 2023 --format xlsx --output ./output
uv run courtlistener-cli audio list --offset 100 --limit 100 --max-pages 2 --format csv --output ./output
```

Count audio records:

```bash
uv run courtlistener-cli audio count
uv run courtlistener-cli audio count --court scotus
uv run courtlistener-cli audio count --court scotus --year 2023
```

Get one audio record:

```bash
uv run courtlistener-cli audio get 123456
```
