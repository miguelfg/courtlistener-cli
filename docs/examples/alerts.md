# Alerts Examples

List search alerts:

```bash
courtlistener-cli alerts list --limit 20
courtlistener-cli alerts list --limit 100 --max-pages 2 --format csv --output ./output
```

Create a search alert:

```bash
courtlistener-cli alerts create --name "Qualified immunity" --query '"qualified immunity"' --rate dly
courtlistener-cli alerts create --name "Patent alerts" --query '"patent infringement"' --rate wly --alert-type search
```

Update an alert:

```bash
courtlistener-cli alerts update --id 123 --name "Updated qualified immunity"
courtlistener-cli alerts update --id 123 --query '"qualified immunity" "summary judgment"' --rate wly
```

Delete an alert:

```bash
courtlistener-cli alerts delete --id 123 --confirm
```
