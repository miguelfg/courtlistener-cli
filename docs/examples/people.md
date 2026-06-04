# People Examples

List people:

```bash
uv run courtlistener-cli people list --limit 20
uv run courtlistener-cli people list --name "Sotomayor" --limit 10
uv run courtlistener-cli people list --name "Smith" --limit 100 --max-pages 2 --offset 100 --format csv --output ./output
```

Count people:

```bash
uv run courtlistener-cli people count
uv run courtlistener-cli people count --name "Sotomayor"
```

Get one person:

```bash
uv run courtlistener-cli people get 1234
```
