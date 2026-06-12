# Positions Examples

List positions:

```bash
courtlistener-cli positions list --limit 20
courtlistener-cli positions list --person 1234 --limit 50
courtlistener-cli positions list --court scotus --order-by date_start --format xlsx --output ./output
courtlistener-cli positions list --person 1234 --court scotus --format json
```

Get one position:

```bash
courtlistener-cli positions get 98765
```
