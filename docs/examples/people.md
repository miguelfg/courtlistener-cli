# People Examples

List people:

```bash
courtlistener-cli people list --limit 20
courtlistener-cli people list --name "Sotomayor" --limit 10
courtlistener-cli people list --name "Smith" --limit 100 --max-pages 2 --offset 100 --format csv --output ./output
```

Count people:

```bash
courtlistener-cli people count
courtlistener-cli people count --name "Sotomayor"
```

Get one person:

```bash
courtlistener-cli people get 1234
```
