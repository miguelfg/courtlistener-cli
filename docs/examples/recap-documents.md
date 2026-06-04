# RECAP Documents Examples

List RECAP documents:

```bash
uv run courtlistener-cli recap-documents list --limit 20
uv run courtlistener-cli recap-documents list --docket-entry 987654 --limit 50
uv run courtlistener-cli recap-documents list --is-available true --order-by date_created --format csv --output ./output
```

Get one RECAP document:

```bash
uv run courtlistener-cli recap-documents get 123456
```

Query by PACER document ID:

```bash
uv run courtlistener-cli recap-documents query --court cand --pacer-doc-id 04512345678
uv run courtlistener-cli recap-documents query --court cand --pacer-doc-id 04512345678 --format xlsx --output ./output
```
