# Examples

These examples show common command patterns and parameter combinations. Replace sample IDs, court IDs, and query text with values from your own workflow.

Common patterns:

```bash
# JSON to terminal
uv run courtlistener-cli opinions list --limit 5

# Save structured output
uv run courtlistener-cli courts list --format csv --output ./output

# Page through larger result sets
uv run courtlistener-cli search query --q '"qualified immunity"' --limit 100 --max-pages 5 --offset 0

# Resume from an offset
uv run courtlistener-cli search query --q '"qualified immunity"' --limit 100 --max-pages 5 --offset 500
```

Use the command-group pages for focused examples.
