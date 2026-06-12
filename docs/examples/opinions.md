# Opinions Examples

List opinions:

```bash
courtlistener-cli opinions list --limit 10
courtlistener-cli opinions list --limit 50 --max-pages 2 --offset 100 --format csv --output ./output
courtlistener-cli opinions list --search "Miranda" --limit 25 --format xlsx --output ./output
```

Count matching opinions:

```bash
courtlistener-cli opinions count
courtlistener-cli opinions count --search "qualified immunity"
```

Get one opinion:

```bash
courtlistener-cli opinions get 123456
courtlistener-cli opinions get 123456 --format json
```
