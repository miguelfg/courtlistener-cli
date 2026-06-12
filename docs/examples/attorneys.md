# Attorneys Examples

List attorneys:

```bash
courtlistener-cli attorneys list --limit 20
courtlistener-cli attorneys list --docket 4134326 --limit 100 --format csv --output ./output
courtlistener-cli attorneys list --docket 4134326 --filter-nested-results --format xlsx --output ./output
```

Get one attorney:

```bash
courtlistener-cli attorneys get 123456
```
