# Financial Disclosure Examples

List disclosure records:

```bash
uv run courtlistener-cli financial list --limit 20
uv run courtlistener-cli financial list --person 1234 --year 2023 --format xlsx --output ./output
uv run courtlistener-cli financial list --year 2022 --limit 100 --max-pages 3 --format csv --output ./output
```

Get one disclosure:

```bash
uv run courtlistener-cli financial get 56789
```

List investments:

```bash
uv run courtlistener-cli financial investments --limit 20
uv run courtlistener-cli financial investments --disclosure 56789 --format json
uv run courtlistener-cli financial investments --redacted false --gross-value-code K --format xlsx --output ./output
```

List gifts:

```bash
uv run courtlistener-cli financial gifts --limit 20
uv run courtlistener-cli financial gifts --disclosure 56789 --redacted false --format csv --output ./output
```

List debts:

```bash
uv run courtlistener-cli financial debts --limit 20
uv run courtlistener-cli financial debts --disclosure 56789 --redacted true --format json
```

List agreements:

```bash
uv run courtlistener-cli financial agreements --limit 20
uv run courtlistener-cli financial agreements --disclosure 56789 --format xlsx --output ./output
```

List non-investment incomes:

```bash
uv run courtlistener-cli financial non-investment-incomes --limit 20
uv run courtlistener-cli financial non-investment-incomes --disclosure 56789 --format csv --output ./output
```

List disclosure positions:

```bash
uv run courtlistener-cli financial disclosure-positions --limit 20
uv run courtlistener-cli financial disclosure-positions --disclosure 56789 --format xlsx --output ./output
```
