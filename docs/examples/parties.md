# Parties Examples

List parties:

```bash
uv run courtlistener-cli parties list --limit 20
uv run courtlistener-cli parties list --docket 4134326 --limit 100 --format json
uv run courtlistener-cli parties list --docket 4134326 --filter-nested-results --format xlsx --output ./output
```
