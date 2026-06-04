# Attorneys Examples

List attorneys:

```bash
uv run courtlistener-cli attorneys list --limit 20
uv run courtlistener-cli attorneys list --docket 4134326 --limit 100 --format csv --output ./output
uv run courtlistener-cli attorneys list --docket 4134326 --filter-nested-results --format xlsx --output ./output
```

Get one attorney:

```bash
uv run courtlistener-cli attorneys get 123456
```
