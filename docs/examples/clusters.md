# Clusters Examples

List opinion clusters:

```bash
courtlistener-cli clusters list --limit 20
courtlistener-cli clusters list --court scotus --limit 50 --format json
courtlistener-cli clusters list --docket 4134326 --format xlsx --output ./output
courtlistener-cli clusters list --docket-number "21-1234" --court ca9 --date-filed-after 2020-01-01 --date-filed-before 2024-12-31
courtlistener-cli clusters list --court ca9 --order-by date_filed --limit 100 --max-pages 3 --format csv --output ./output
```

Get one cluster:

```bash
courtlistener-cli clusters get 123456
courtlistener-cli clusters get 123456 --format json
```

Count clusters:

```bash
courtlistener-cli clusters count
courtlistener-cli clusters count --court scotus
courtlistener-cli clusters count --docket 4134326 --court ca9
```
