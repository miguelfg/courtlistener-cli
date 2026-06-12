# Audio Examples

List oral arguments:

```bash
courtlistener-cli audio list --limit 20
courtlistener-cli audio list --court scotus --limit 50
courtlistener-cli audio list --court ca9 --year 2023 --format xlsx --output ./output
courtlistener-cli audio list --offset 100 --limit 100 --max-pages 2 --format csv --output ./output
```

Count audio records:

```bash
courtlistener-cli audio count
courtlistener-cli audio count --court scotus
courtlistener-cli audio count --court scotus --year 2023
```

Get one audio record:

```bash
courtlistener-cli audio get 123456
```
