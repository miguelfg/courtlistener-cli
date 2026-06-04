# Clusters Examples

List opinion clusters:

```bash
uv run courtlistener-cli clusters list --limit 20
uv run courtlistener-cli clusters list --court scotus --limit 50 --format json
uv run courtlistener-cli clusters list --docket 4134326 --format xlsx --output ./output
uv run courtlistener-cli clusters list --docket-number "21-1234" --court ca9 --date-filed-after 2020-01-01 --date-filed-before 2024-12-31
uv run courtlistener-cli clusters list --court ca9 --order-by date_filed --limit 100 --max-pages 3 --format csv --output ./output
```

Get one cluster:

```bash
uv run courtlistener-cli clusters get 123456
uv run courtlistener-cli clusters get 123456 --format json
```

Count clusters:

```bash
uv run courtlistener-cli clusters count
uv run courtlistener-cli clusters count --court scotus
uv run courtlistener-cli clusters count --docket 4134326 --court ca9
```
