# Docket Alert Examples

List docket alerts:

```bash
courtlistener-cli docket-alerts list --limit 20
courtlistener-cli docket-alerts list --limit 100 --max-pages 2 --format xlsx --output ./output
```

Create a docket alert:

```bash
courtlistener-cli docket-alerts create --docket 4134326
courtlistener-cli docket-alerts create --docket 4134326 --alert-type 2
```

Delete a docket alert:

```bash
courtlistener-cli docket-alerts delete --id 123 --confirm
```
