# CourtListener Python CLI Client

Python CLI tool for accessing the CourtListener REST API with support for legal data queries, batch processing, and multiple output formats.

## Features

- **40+ API Resources**: Access opinions, dockets, PACER data, judges, disclosures, and more
- **Batch Processing**: Process CSV/JSON Lines batch files with pagination support
- **Multiple Outputs**: Export results as JSON, CSV, or XLSX
- **Configuration Management**: Secure API token and settings via .env file
- **Comprehensive Logging**: DEBUG-level logging for troubleshooting
- **Production Ready**: Full error handling and retry strategies

## Installation

```bash
# Using uv (recommended)
make install

# Or manually
uv pip install -e .
```

## Quick Start

### 1. Configure API Token

```bash
cp .env.example .env
# Edit .env and add your CourtListener API token
export COURTLISTENER_API_TOKEN=your_token_here
```

### 2. Run Commands

```bash
# List opinions
courtlistener-cli opinions list --limit 10

# Get a specific opinion
courtlistener-cli opinions get 123456

# Export to XLSX
courtlistener-cli opinions list --format xlsx --output ./results/
```

### 3. Batch Processing

```bash
# Create batch file
echo 'method,endpoint,limit\nGET,/opinions/,20' > data/batch.csv

# Process batch
courtlistener-cli batch --input-file data/batch.csv --format xlsx
```

## Configuration

### Environment Variables

Create `.env` file with:

```bash
COURTLISTENER_API_TOKEN=your_token_here
COURTLISTENER_BASE_URL=https://www.courtlistener.com/api/rest/v4
COURTLISTENER_TIMEOUT=30
LOG_LEVEL=DEBUG
OUTPUT_FORMAT=xlsx
INCLUDE_TIMESTAMP=true
```

## Available Commands

### opinions
- `opinions list` - List opinions with pagination
- `opinions get <id>` - Get single opinion details

### batch
- `batch` - Process batch files (CSV/JSON Lines)

## Output Formats

- **JSON**: Full structured data
- **CSV**: Tabular format (auto-flattened nested data)
- **XLSX**: Excel workbooks with formatted headers

## Development

```bash
# Install dev dependencies
make install-dev

# Run linting and formatting
make lint
make format

# Run tests
make test

# View all make targets
make help
```

## API Documentation

See [CourtListener API Docs](https://www.courtlistener.com/help/api/rest/) for full endpoint reference.

## Support

For issues or questions:
1. Check API authentication and token
2. Enable DEBUG logging: `export LOG_LEVEL=DEBUG`
3. Review logs in `logs/` directory
4. Contact CourtListener support

## License

CC0 1.0 Universal (same as CourtListener API)
