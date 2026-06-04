# Authentication

CourtListener API requests need an API token for authenticated endpoints and higher limits.

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Set your token:

```bash
COURTLISTENER_API_TOKEN=your-token-here
```

You can also export it in your shell:

```bash
export COURTLISTENER_API_TOKEN=your-token-here
```

Use `LOG_LEVEL=DEBUG` when troubleshooting request behavior.
