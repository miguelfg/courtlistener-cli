# API Python Client - Product Requirements Document

## Table of Contents

1. [Introduction](#introduction)
2. [Implementation Decisions](#implementation-decisions)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Authentication](#authentication)
6. [Endpoint Reference](#endpoint-reference)
7. [Input/Output Examples](#inputoutput-examples)
8. [Caching](#caching)
9. [Rate Limiting](#rate-limiting)
10. [Error Handling](#error-handling)
11. [Logging](#logging)
12. [Best Click Practices](#best-click-practices)
13. [Makefile & Project Management](#makefile--project-management)
14. [Implementation Checklist](#implementation-checklist)

---

## Introduction

### Overview

This document describes the Product Requirements for a Python CLI client for **[API Name]**. The client provides a command-line interface to interact with the API, supporting batch processing, caching, rate limiting, and comprehensive error handling.

### Purpose

- Enable Python developers to quickly integrate **[API Name]** into applications
- Provide a user-friendly CLI tool for querying API endpoints
- Support batch operations for large-scale data processing
- Implement best practices for API interactions (caching, retry logic, rate limit handling)

### Target Audience

- Python developers building applications with **[API Name]**
- Data engineers processing data from the API
- DevOps engineers integrating the API into pipelines

### Key Features

- ✓ Complete endpoint coverage for all API operations
- ✓ Multiple output formats (JSON, CSV, XLSX)
- ✓ Batch processing support (CSV/JSONL input)
- ✓ Built-in caching to reduce API calls
- ✓ Automatic retry logic with exponential backoff
- ✓ Rate limiting respects API quota
- ✓ Comprehensive logging for debugging
- ✓ Configuration management via CLI and files

---

## Implementation Decisions

Capture user-confirmed decisions from `skills/doc-to-prd/assets/questions.md`:

- CLI Name: `[cli-name]`
- Python Version: `[python-version-policy]`
- HTTP Library: `[requests|httpx|aiohttp|urllib3]`
- Authentication: `[derived from API/OpenAPI source]`
- Credentials Configuration: `[env_vars|config|interactive_prompt]`
- Timeout: `[timeout-policy]`
- Retry Policy: `[retry-policy]`
- Output Formats: `[json,csv,xlsx,sqlite]`
- Output Accepted Formats and Default: `[default_xlsx__accepted_xlsx|default_xlsx__accepted_xlsx_csv|default_xlsx__accepted_xlsx_sqlite|default_xlsx__accepted_xlsx_csv_sqlite]`
- Batch Input Formats: `[csv|txt|both|none]`
- Default Save Data Mode: `[timestamped|overwrite|append_with_request_timestamp]`
- Lint/Format Toolchain: `ruff check --fix` + `ruff format`

This section is the source of truth for `prd-to-cli` generation.

---

## Installation

### System Requirements

- Python 3.8+
- uv (recommended Python package/project manager)
- curl (optional, for manual API testing)

### Installation Methods

#### Recommended (uv)

```bash
git clone https://github.com/[org]/[api-client].git
cd [api-client]
uv sync
```

#### Alternative (pip)

```bash
pip install [api-client]
```

### Verify Installation

```bash
uv run [cli-name] --version
uv run [cli-name] --help
```

### Validation Requirements

The generated CLI project must include live smoke validation for read-oriented commands during the `prd-to-cli` step.

Required validation behavior:
- Run low-volume GET/list validation against each generated read/list command or GET endpoint mapping.
- Prefer list/read commands that do not require fabricated identifiers.
- Limit the returned records to a small number such as `10` whenever the API supports pagination or limit-style parameters.
- Use the API's documented parameter names such as `limit`, `page_size`, `per_page`, or equivalent instead of inventing new flags.
- Treat these live read validations as required acceptance checks, not optional extras.

### Dependencies

The client requires:
- **[HTTP_LIBRARY]** ≥ [MIN_VERSION] — HTTP client library (from Implementation Decisions)
- **click** ≥ 8.1.0 — CLI framework
- **pandas** ≥ 1.5.0 — Data manipulation
- **python-dotenv** ≥ 0.21.0 — Environment configuration

All dependencies are automatically installed with the package.

---

## Configuration

### Environment Variables

Configure the client using environment variables:

```bash
# Required
[API_PREFIX]_API_KEY=your-api-key-here

# Optional
[API_PREFIX]_BASE_URL=https://api.example.com
[API_PREFIX]_TIMEOUT=30
[API_PREFIX]_VERBOSE=false
[API_PREFIX]_CACHE_DIR=./cache
```

### Configuration File

Configuration is also stored in `.[cli-name]_settings.json`:

```json
{
  "api_key": "your-api-key",
  "base_url": "https://api.example.com",
  "timeout": 30,
  "cache_enabled": true,
  "cache_ttl": 3600,
  "log_level": "INFO",
  "output_format": "json",
  "verbose": false
}
```

### Configuration Management Commands

```bash
# Show current configuration
[cli-name] config show

# Set a configuration value
[cli-name] config set api_key your-new-key

# Reset to defaults
[cli-name] config reset

# Show cache directory
[cli-name] config show --include-cache
```

### Priority Order

1. CLI flags (highest priority)
2. Environment variables
3. Configuration file
4. Default values (lowest priority)

---

## Authentication

### API Key Authentication

The client uses API key authentication by default:

```bash
# Via environment variable
export [API_PREFIX]_API_KEY=your-api-key-here

# Via CLI configuration
[cli-name] config set api_key your-api-key-here

# Via command flag (temporary override)
[cli-name] endpoint-name --api-key your-api-key-here
```

### Authentication Methods

**Method 1: Environment Variable (Recommended)**

```bash
export [API_PREFIX]_API_KEY="sk_live_xxxxxxxxxxxx"
[cli-name] users list
```

**Method 2: Configuration File**

Edit `.[cli-name]_settings.json`:
```json
{
  "api_key": "sk_live_xxxxxxxxxxxx"
}
```

**Method 3: CLI Flag (Temporary)**

```bash
[cli-name] users list --api-key sk_live_xxxxxxxxxxxx
```

### Error Handling

- **Missing API Key:** Error message with setup instructions
- **Invalid API Key:** HTTP 401 response, check key validity
- **Expired Token:** Re-authenticate with new key
- **Rate Limited:** Automatic retry with backoff

### Best Practices

✓ Never hardcode API keys in scripts
✓ Use environment variables or config files
✓ Rotate keys regularly
✓ Use role-based keys with minimal permissions
✓ Keep keys in .gitignore

---

## Endpoint Reference

### Resource Naming

Each API resource corresponds to a Click command group:

- **Resource:** Users → Command: `[cli-name] users`
- **Resource:** Posts → Command: `[cli-name] posts`
- **Resource:** Comments → Command: `[cli-name] comments`

### Endpoint Structure

Each endpoint includes:

```
Method: HTTP method (GET, POST, PUT, DELETE, PATCH)
Path: API endpoint path
Description: What the endpoint does
Parameters:
  - Path: URL path parameters (required in URL)
  - Query: Query string parameters (optional filters)
  - Body: Request body fields (for POST/PUT/PATCH)
Response: Expected response structure
Example: Code example using the CLI
```

### Standard Endpoints

#### List Resources

```
Method: GET
Path: /resource
Description: Retrieve a list of resources
Parameters:
  - Query: limit, offset, sort, filter
Response: Array of resource objects
Example:
  [cli-name] resource list --limit 10
```

#### Get Single Resource

```
Method: GET
Path: /resource/{id}
Description: Retrieve a specific resource by ID
Parameters:
  - Path: id (required)
Response: Single resource object
Example:
  [cli-name] resource get --id 123
```

#### Create Resource

```
Method: POST
Path: /resource
Description: Create a new resource
Parameters:
  - Body: Resource fields (name, email, etc.)
Response: Created resource with ID
Example:
  [cli-name] resource create --name "John" --email "john@example.com"
```

#### Update Resource

```
Method: PUT
Path: /resource/{id}
Description: Update an existing resource
Parameters:
  - Path: id (required)
  - Body: Fields to update
Response: Updated resource object
Example:
  [cli-name] resource update --id 123 --name "Jane"
```

#### Delete Resource

```
Method: DELETE
Path: /resource/{id}
Description: Delete a resource
Parameters:
  - Path: id (required)
Response: Success confirmation
Example:
  [cli-name] resource delete --id 123 --confirm
```

### Detailed Endpoint Documentation

#### [RESOURCE_NAME]

**List [Resource]**
- Command: `[cli-name] [resource] list`
- Method: GET
- Path: `/[resource]`
- Description: Retrieve paginated list of [resource] objects
- Parameters:
  - `--limit`: Results per page (default: 20, max: 100)
  - `--offset`: Starting position for pagination (default: 0)
  - `--sort`: Sort field and direction (default: -created_at)
  - `--filter`: Filter query (e.g., status=active)
- Response: Array of [resource] objects with pagination info
- Code Example:
  ```bash
  # List first 10 resources
  [cli-name] [resource] list --limit 10

  # List with filter
  [cli-name] [resource] list --filter status=active

  # Save to file
  [cli-name] [resource] list --output-file resources.json
  ```

**Get [Resource] by ID**
- Command: `[cli-name] [resource] get`
- Method: GET
- Path: `/[resource]/{id}`
- Description: Retrieve a specific [resource] by ID
- Parameters:
  - `--id`: Resource ID (required)
  - `--format`: Output format (json, csv, xlsx)
- Response: Single [resource] object
- Code Example:
  ```bash
  [cli-name] [resource] get --id abc123
  [cli-name] [resource] get --id abc123 --format json
  ```

**Create [Resource]**
- Command: `[cli-name] [resource] create`
- Method: POST
- Path: `/[resource]`
- Description: Create a new [resource]
- Parameters:
  - `--name`: Resource name (required)
  - `--field1`: Additional field (optional)
  - `--field2`: Additional field (optional)
- Response: Created [resource] with ID
- Code Example:
  ```bash
  [cli-name] [resource] create --name "My Resource" --field1 "value1"
  ```

**Update [Resource]**
- Command: `[cli-name] [resource] update`
- Method: PUT
- Path: `/[resource]/{id}`
- Description: Update an existing [resource]
- Parameters:
  - `--id`: Resource ID (required)
  - `--name`: New name (optional)
  - `--field1`: Updated field (optional)
- Response: Updated [resource] object
- Code Example:
  ```bash
  [cli-name] [resource] update --id abc123 --name "Updated Name"
  ```

**Delete [Resource]**
- Command: `[cli-name] [resource] delete`
- Method: DELETE
- Path: `/[resource]/{id}`
- Description: Delete a [resource]
- Parameters:
  - `--id`: Resource ID (required)
  - `--confirm`: Confirm deletion (safety flag)
- Response: Success message
- Code Example:
  ```bash
  [cli-name] [resource] delete --id abc123 --confirm
  ```

---

## Input/Output Examples

### Single Request Examples

#### List Users

**Command:**
```bash
[cli-name] users list --limit 5
```

**Output (JSON):**
```json
{
  "users": [
    {
      "id": "user_1",
      "name": "Alice Smith",
      "email": "alice@example.com",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "user_2",
      "name": "Bob Johnson",
      "email": "bob@example.com",
      "created_at": "2024-01-16T14:20:00Z"
    }
  ],
  "total": 2,
  "limit": 5,
  "offset": 0
}
```

**Output (CSV):**
```csv
id,name,email,created_at
user_1,Alice Smith,alice@example.com,2024-01-15T10:30:00Z
user_2,Bob Johnson,bob@example.com,2024-01-16T14:20:00Z
```

#### Create User

**Command:**
```bash
[cli-name] users create --name "Charlie Brown" --email "charlie@example.com"
```

**Response:**
```json
{
  "id": "user_3",
  "name": "Charlie Brown",
  "email": "charlie@example.com",
  "created_at": "2024-01-17T09:15:00Z",
  "status": "active"
}
```

### Batch Processing Examples

#### Batch Input File (CSV)

**File: `requests.csv`**
```csv
method,endpoint,id,name,email
GET,/users,user_1,,
GET,/users,user_2,,
POST,/users,,David Lee,david@example.com
PUT,/users,user_1,Updated Name,updated@example.com
```

**Command:**
```bash
[cli-name] batch process --input requests.csv --format csv
```

#### Batch Input File (JSON Lines)

**File: `requests.jsonl`**
```jsonl
{"method": "GET", "endpoint": "/users", "id": "user_1"}
{"method": "GET", "endpoint": "/users", "id": "user_2"}
{"method": "POST", "endpoint": "/users", "name": "David Lee", "email": "david@example.com"}
{"method": "PUT", "endpoint": "/users", "id": "user_1", "name": "Updated Name"}
```

**Command:**
```bash
[cli-name] batch process --input requests.jsonl
```

#### Batch Output

**File: `output/results_20240115_143000.xlsx`**
Contains tabs for:
- Summary (total requests, success count, errors)
- Results (response for each request)
- Errors (detailed error information)

### Output Format Examples

#### JSON (Default)

```bash
[cli-name] users get --id user_1 --format json
```

```json
{
  "id": "user_1",
  "name": "Alice Smith",
  "email": "alice@example.com",
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### CSV

```bash
[cli-name] users list --format csv
```

```
id,name,email,status,created_at
user_1,Alice Smith,alice@example.com,active,2024-01-15T10:30:00Z
```

#### XLSX

```bash
[cli-name] users list --format xlsx --output-file users.xlsx
```

Opens in Excel with formatted columns and headers.

---

## Caching

### Overview

The client caches API responses to:
- Reduce API calls and improve performance
- Lower API quota usage
- Enable offline-like operation for recent data

### Cache Configuration

**Enable/Disable Caching:**

```bash
# Check cache status
[cli-name] config show | grep cache_enabled

# Disable caching (temporary)
[cli-name] users list --no-cache

# Disable caching (permanent)
[cli-name] config set cache_enabled false
```

**Cache Location:**

```bash
# Default: ~/.cache/[cli-name]/
# Custom location:
[cli-name] config set cache_dir /custom/cache/path
```

**Cache TTL (Time-To-Live):**

```bash
# View current TTL (default: 3600 seconds / 1 hour)
[cli-name] config show | grep cache_ttl

# Set custom TTL (in seconds)
[cli-name] config set cache_ttl 7200  # 2 hours
```

### Cache Management Commands

```bash
# List cached items
[cli-name] cache list

# Get cache statistics
[cli-name] cache info

# Clear specific cache entry
[cli-name] cache delete --key user_1

# Clear all cache
[cli-name] cache clear --confirm

# View cache size
du -sh ~/.cache/[cli-name]/
```

### Cache Strategy

**Cache Key Generation:**
- Method + Endpoint + Query Parameters (hashed)
- Example key: `GET:users:list:9a3c5d2f`

**Cache Validation:**
- Check TTL on cache hit
- If expired: Fetch fresh data
- If valid: Return cached response

**Cache Bypass:**
```bash
# Force fresh data (bypass cache)
[cli-name] users list --override
```

### Best Practices

✓ Enable caching for read-only operations (GET)
✓ Disable for critical/real-time data
✓ Use appropriate TTL based on data freshness needs
✓ Clear cache if experiencing stale data issues
✓ Monitor cache size and clean periodically

---

## Rate Limiting

### API Rate Limits

The [API Name] API enforces rate limits:
- **Requests per minute:** [Limit]
- **Requests per hour:** [Limit]
- **Burst limit:** [Limit]

### Client Rate Limiting

The client implements automatic rate limiting:

**Courtesy Delay:**
- 100ms delay between requests to public APIs
- Prevents rate limit violations
- Can be adjusted via configuration

**Automatic Retry on Rate Limit:**
- Detects HTTP 429 (Too Many Requests)
- Implements exponential backoff
- Max retries: 3
- Initial delay: 1 second, then 2s, 4s
- Jitter: ±10% randomization

### Configuration

```bash
# View rate limit settings
[cli-name] config show | grep -E "retry|backoff|delay"

# Set custom retry attempts
[cli-name] config set max_retries 5

# Set custom backoff multiplier
[cli-name] config set backoff_multiplier 1.5

# Disable courtesy delay
[cli-name] config set courtesy_delay 0
```

### Example: Rate Limit Handling

```bash
# This command will auto-retry if rate limited
[cli-name] users list

# Output includes retry information (with --verbose)
[cli-name] users list --verbose
# [INFO] Rate limited (429), retrying in 1.2 seconds...
# [INFO] Retry 1/3 successful
```

### Rate Limit Best Practices

✓ Use caching to reduce requests
✓ Process data in batches when possible
✓ Respect courtesy delays between requests
✓ Monitor rate limit headers in responses
✓ Set up alerts for frequent rate limits
✗ Don't disable retry logic
✗ Don't make rapid repeated requests

---

## Error Handling

### Error Classification

**Network Errors** (Retriable)
- HTTP 5xx (Server errors)
- Connection timeouts
- DNS failures
- Action: Automatic retry with exponential backoff

**Rate Limit Errors** (Retriable)
- HTTP 429 (Too Many Requests)
- Action: Automatic retry with longer backoff

**Client Errors** (Non-retriable)
- HTTP 400 (Bad Request)
- HTTP 401 (Unauthorized)
- HTTP 403 (Forbidden)
- HTTP 404 (Not Found)
- Action: Display error message, do not retry

**Data Errors** (Exception)
- Malformed JSON in response
- Missing required fields
- Type mismatches
- Action: Raise exception with details

### Error Response Format

```json
{
  "error": {
    "code": "invalid_request",
    "message": "User not found",
    "details": {
      "field": "user_id",
      "expected": "string",
      "received": "integer"
    },
    "status": 404,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/missing API key | Check API key in config |
| 403 Forbidden | Insufficient permissions | Verify key has required scope |
| 404 Not Found | Resource doesn't exist | Check resource ID/endpoint |
| 429 Too Many Requests | Rate limit exceeded | Wait, then retry (automatic) |
| 500 Server Error | API server issue | Retry later (automatic) |
| Connection timeout | Network issue | Check connectivity, retry |

### Error Handling in Code

**Using try-except:**

```bash
# This will handle errors gracefully
[cli-name] users get --id invalid_id 2>&1

# Output:
# Error: User not found (404)
# Use --verbose for details
```

**With verbose output:**

```bash
[cli-name] users get --id invalid_id --verbose

# Output includes full stack trace and request/response
```

### Best Practices

✓ Always check command output for errors
✓ Use `--verbose` flag for debugging
✓ Review error messages carefully
✓ Check logs for detailed error information
✓ Validate input before submitting
✗ Ignore error messages
✗ Retry immediately on client errors
✗ Hardcode error handling

---

## Logging

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Detailed diagnostic info | Full request/response payloads |
| INFO | General info messages | API calls, cache hits, timing |
| WARNING | Warning messages | Deprecated endpoints, slow requests |
| ERROR | Error messages | Failed requests, validation errors |

### Configuration

**Set log level:**

```bash
# Via config
[cli-name] config set log_level DEBUG

# Via environment variable
export [API_PREFIX]_LOG_LEVEL=DEBUG

# Via CLI flag
[cli-name] users list --log-level DEBUG
```

**View logs:**

```bash
# Log file location
~/.cache/[cli-name]/[cli-name].log

# Follow logs in real-time
tail -f ~/.cache/[cli-name]/[cli-name].log

# View logs with grep
grep ERROR ~/.cache/[cli-name]/[cli-name].log
```

### Log Format

```
2024-01-15 10:30:45,123 - [cli-name] - INFO - GET /users (0.45s, cached=false)
2024-01-15 10:30:46,234 - [cli-name] - DEBUG - Response: {"users": [...], "total": 100}
2024-01-15 10:30:47,345 - [cli-name] - INFO - Request completed in 2.222s
```

### Verbose Mode

```bash
# Enable verbose/debug output
[cli-name] users list --verbose

# Output includes:
# - Full request URL and headers
# - Request/response payloads
# - Cache hit/miss status
# - Execution timing
# - Retry attempts
```

### Best Practices

✓ Use appropriate log levels
✓ Review logs for debugging
✓ Rotate logs periodically
✓ Archive logs for auditing
✓ Use verbose mode when troubleshooting
✗ Log sensitive data (API keys, tokens)
✗ Leave debug logging in production

---

## Best Click Practices

### CLI Command Design

**Use click options, not arguments:**

```bash
# ✓ Good: clear, discoverable with --help
[cli-name] users get --id abc123

# ✗ Bad: unclear, user has to know argument position
[cli-name] users get abc123
```

**Group related commands:**

```bash
# ✓ Good: logical organization
[cli-name] users list
[cli-name] users get
[cli-name] users create

# ✗ Bad: flat structure
[cli-name] list_users
[cli-name] get_user
[cli-name] create_user
```

**Add helpful defaults:**

```bash
# ✓ Sensible defaults
uv run [cli-name] users list  # Defaults to limit=20, format=json

# Explicit override
uv run [cli-name] users list --limit 50 --format csv
```

**Provide clear help text:**

```bash
uv run [cli-name] --help
uv run [cli-name] users --help
uv run [cli-name] users list --help
```

### Standard Options

**All commands should support:**

```
--format (json|csv|xlsx)      Output format
--output-file PATH            Save output to file
--verbose                      Show detailed output
--api-key KEY                  Override API key
--timeout SECONDS              Request timeout
```

**List commands should support:**

```
--limit N                      Number of results
--offset N                     Starting position
--sort FIELD                   Sort by field
--filter QUERY                 Filter expression
```

**Modification commands should support:**

```
--dry-run                      Show what would happen
--confirm                      Confirm destructive action
--override                     Force operation
```

### Error Messages

**Clear and actionable:**

```
✓ Error: User not found (ID: abc123)
✓ Solution: Check the ID and try again, or use 'users list' to find valid IDs

✗ Error: 404
✗ Solution: Retry
```

**Include suggestions:**

```bash
Error: API key not configured
Use one of:
  1. Set environment: export [API_PREFIX]_API_KEY=your-key
  2. Configure: [cli-name] config set api_key your-key
  3. Pass flag: [cli-name] users list --api-key your-key
```

### Performance Best Practices

✓ Use caching for repeated queries
✓ Batch operations when possible
✓ Use filters to reduce data transfer
✓ Process data in chunks for large datasets
✓ Set appropriate timeout values
✗ Make unnecessary API calls
✗ Process all data in memory at once
✗ Set timeout too short or too long

---

## Makefile & Project Management

### Project Structure

```
[api-client]/
├── Makefile                    # Common tasks
├── pyproject.toml              # Project metadata (with uv configuration)
├── uv.lock                     # Locked dependencies
├── README.md                   # Project documentation
├── src/
│   └── [cli_name]/
│       ├── __init__.py
│       ├── cli.py              # Click CLI entry point
│       ├── client.py           # HTTP client
│       ├── config.py           # Configuration management
│       ├── cache.py            # Caching logic
│       ├── logger.py           # Logging setup
│       └── commands/           # Click command groups
│           ├── users.py
│           ├── posts.py
│           └── ...
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_client.py
│   └── test_integration.py
├── examples/
│   ├── batch_requests.csv
│   ├── basic_usage.sh
│   └── advanced_usage.sh
└── docs/
    ├── INSTALLATION.md
    ├── USAGE.md
    └── API_REFERENCE.md
```

### Makefile Commands

The generated project includes a Makefile using `uv` (Python package and project manager):

**Installation & Setup:**

```bash
make install           # Install dependencies with uv sync
make install-dev       # Install with dev dependencies
```

**Development:**

```bash
make lint             # Run code linting
make format           # Format code
make test             # Run unit tests
make test-cov         # Run tests with coverage
```

**CLI Testing:**

```bash
make users-list       # Example: uv run [cli-name] users list
make users-get        # Example: uv run [cli-name] users get --id 123
make posts-create     # Example: uv run [cli-name] posts create --title "..."
```

**Building & Release:**

```bash
make build            # Build distribution packages
make clean            # Clean build artifacts
make release          # Build and prepare release
```

**Project Management:**

```bash
make help             # Show all available commands
make status           # Show project status
```

### Using uv (Python Package Manager)

**uv** is a fast, reliable Python package manager and project manager:

**Installation:**

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

**Project Setup:**

```bash
# Initialize new project
uv init [project-name]

# Or in existing project
uv sync

# Add dependencies
uv add requests click pandas

# Add dev dependencies
uv add --dev pytest black pylint
```

**Running Commands:**

```bash
# Run CLI commands
uv run [cli-name] --help
uv run [cli-name] users list
uv run [cli-name] batch --input data/batch.csv

# Run tests
uv run pytest tests/ -v

# Run linters
uv run black src/
uv run pylint src/
```

**Project Configuration (pyproject.toml):**

```toml
[project]
name = "[cli-name]"
version = "1.0.0"
description = "Python CLI client for [API Name]"
requires-python = ">=3.8"
dependencies = [
    "click>=8.1.0",
    "requests>=2.28.0",
    "pandas>=1.5.0",
    "python-dotenv>=0.21.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "pylint>=2.17",
    "isort>=5.0",
]

[project.scripts]
[cli-name] = "[cli_name].cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

### Sample Makefile with uv

```makefile
.PHONY: help install install-dev lint format test test-cov clean build release

PROJECT_NAME := [cli-name]

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies (uv sync)"
	@echo "  make install-dev    - Install with dev dependencies"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code"
	@echo "  make test           - Run tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make build          - Build distribution"
	@echo "  make release        - Prepare release"
	@echo ""
	@echo "Endpoint examples:"
	@echo "  make users-list     - uv run $(PROJECT_NAME) users list"
	@echo "  make users-get      - uv run $(PROJECT_NAME) users get --id 123"
	@echo "  make posts-create   - uv run $(PROJECT_NAME) posts create --title '...'"

install:
	uv sync

install-dev:
	uv sync --all-extras

lint:
	uv run black --check src/
	uv run pylint src/

format:
	uv run black src/
	uv run isort src/

test:
	uv run pytest tests/ -v

test-cov:
	uv run pytest tests/ -v --cov=src/

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage

build:
	uv build

release: clean build
	@echo "Release artifacts ready in dist/"
	@ls -lh dist/

# Endpoint example targets
users-list:
	uv run $(PROJECT_NAME) users list

users-get:
	uv run $(PROJECT_NAME) users get --id 123

posts-create:
	uv run $(PROJECT_NAME) posts create --title "Example"

.DEFAULT_GOAL := help
```

### Common Workflow with uv

**Development:**

```bash
# 1. Clone and sync
git clone <repo>
cd [api-client]
uv sync

# 2. Make changes
vim src/[cli-name]/...

# 3. Run tests
uv run pytest tests/ -v

# 4. Format code
uv run black src/
uv run isort src/

# 5. Test CLI
uv run [cli-name] --help

# 6. Commit and push
git add .
git commit -m "Feature: ..."
git push
```

**Release:**

```bash
# 1. Update version in pyproject.toml
vim pyproject.toml

# 2. Build and test
uv build
uv run pytest tests/ -v

# 3. Create tag
git tag v1.0.0
git push --tags

# 4. Upload to PyPI
uv publish
```

### Benefits of uv

✓ **Fast** — 10x faster than pip for common operations
✓ **Reliable** — Deterministic builds with lock file
✓ **Simple** — Single tool for install, run, build, publish
✓ **Python-native** — Works with standard Python projects
✓ **Batteries included** — Package management + project management

---

## Implementation Checklist

Use this checklist during implementation and review. These items were derived from issues observed in existing example CLIs.

- [ ] Do not shadow imported class/function names (for example, avoid redefining `Config` in a module that already imports `Config`).
- [ ] Ensure all advertised output formats are fully implemented (`json`, `csv`, `xlsx`) for both single commands and batch mode.
- [ ] Ensure batch request execution respects per-row HTTP method (`GET`, `POST`, `PUT/PATCH`, `DELETE`) instead of forcing one method.
- [ ] Avoid broad `except Exception`; catch expected exception types and return actionable user-facing errors.
- [ ] Use structured logging (and `click.echo` for CLI output) instead of raw `print()` in runtime paths.
- [ ] Parse `.env` defensively (skip malformed lines, comments, blank values) to avoid `split`/parse crashes.
- [ ] Define file I/O explicitly with encoding/newline policy (for example, UTF-8 and CSV-safe writes).
- [ ] Handle non-JSON/empty API responses safely before calling `.json()`.
- [ ] Keep authentication header names and auth schemes configurable per API (`X-API-Key`, `Authorization`, provider-specific headers).
- [ ] Validate and normalize base URL and endpoint joining to prevent malformed URLs.
- [ ] Avoid hidden placeholders like “format not yet implemented” in generated command handlers.
- [ ] Add coverage for error paths: auth failures, timeouts, retries exhausted, malformed batch rows, and invalid output paths.
- [ ] Add integration/smoke tests that verify generated files and CLI behavior end-to-end (not only `--help`/dry-run).
- [ ] Specify deterministic defaults for retry/backoff/timeouts and expose overrides via config/flags.
- [ ] Ensure generated project metadata is complete (`pyproject.toml`, console script entry point, dependencies).

---

## Summary

This PRD provides a comprehensive guide for developing and using a Python CLI client for the [API Name] API. It covers:

- Installation and setup procedures
- Configuration and authentication methods
- Complete endpoint reference with examples
- Advanced features (caching, rate limiting, error handling, logging)
- Best practices for CLI design and usage
- Project management with Makefile and uvicorn

For additional help, run:

```bash
uv run [cli-name] --help
uv run [cli-name] <command> --help
uv run [cli-name] --version
```
