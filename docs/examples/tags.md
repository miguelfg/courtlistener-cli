# Tags Examples

List tags:

```bash
uv run courtlistener-cli tags list --limit 20
uv run courtlistener-cli tags list --limit 100 --max-pages 2 --format csv --output ./output
uv run courtlistener-cli tags list --format xlsx --output ./output
```

Get one tag:

```bash
uv run courtlistener-cli tags get 123
```
