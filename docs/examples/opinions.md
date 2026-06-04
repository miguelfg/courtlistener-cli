# Opinions Examples

List opinions:

```bash
uv run courtlistener-cli opinions list --limit 10
uv run courtlistener-cli opinions list --limit 50 --max-pages 2 --offset 100 --format csv --output ./output
uv run courtlistener-cli opinions list --search "Miranda" --limit 25 --format xlsx --output ./output
```

Count matching opinions:

```bash
uv run courtlistener-cli opinions count
uv run courtlistener-cli opinions count --search "qualified immunity"
```

Get one opinion:

```bash
uv run courtlistener-cli opinions get 123456
uv run courtlistener-cli opinions get 123456 --format json
```
