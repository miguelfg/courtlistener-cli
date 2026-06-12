# Financial Disclosure Examples

List disclosure records:

```bash
courtlistener-cli financial list --limit 20
courtlistener-cli financial list --person 1234 --year 2023 --format xlsx --output ./output
courtlistener-cli financial list --year 2022 --limit 100 --max-pages 3 --format csv --output ./output
```

Get one disclosure:

```bash
courtlistener-cli financial get 56789
```

List investments:

```bash
courtlistener-cli financial investments --limit 20
courtlistener-cli financial investments --disclosure 56789 --format json
courtlistener-cli financial investments --redacted false --gross-value-code K --format xlsx --output ./output
```

List gifts:

```bash
courtlistener-cli financial gifts --limit 20
courtlistener-cli financial gifts --disclosure 56789 --redacted false --format csv --output ./output
```

List debts:

```bash
courtlistener-cli financial debts --limit 20
courtlistener-cli financial debts --disclosure 56789 --redacted true --format json
```

List agreements:

```bash
courtlistener-cli financial agreements --limit 20
courtlistener-cli financial agreements --disclosure 56789 --format xlsx --output ./output
```

List non-investment incomes:

```bash
courtlistener-cli financial non-investment-incomes --limit 20
courtlistener-cli financial non-investment-incomes --disclosure 56789 --format csv --output ./output
```

List disclosure positions:

```bash
courtlistener-cli financial disclosure-positions --limit 20
courtlistener-cli financial disclosure-positions --disclosure 56789 --format xlsx --output ./output
```
