# Docket Entries Examples

List entries for a docket:

```bash
courtlistener-cli docket-entries list --docket 4134326 --limit 20
courtlistener-cli docket-entries list --docket 4134326 --limit 100 --max-pages 3 --order-by date_filed
courtlistener-cli docket-entries list --docket 4134326 --format xlsx --output ./output
```

Get one docket entry:

```bash
courtlistener-cli docket-entries get 987654
```
