# Generated Project Structure

When you run the skill, it generates a complete Python Click CLI project with the following structure:

## Full Directory Layout

```
my_api_client/
├── Makefile                   # Common development commands
├── src/
│   ├── __init__.py
│   ├── cli.py                 # Main CLI entry point
│   ├── client.py              # HTTP client library
│   ├── config.py              # Configuration management
│   ├── batch_processor.py      # Batch request processor
│   ├── logger.py              # Logging helpers
│   ├── output.py              # Export/output helpers
│   ├── utils.py               # Shared utility helpers
│   └── commands/
│       ├── __init__.py
│       ├── pets_commands.py    # One file per API resource
│       ├── orders_commands.py
│       └── users_commands.py
├── tests/
│   ├── __init__.py
│   └── test_cli.py            # CLI smoke tests
├── data/                      # Input batch files (user-provided)
│   ├── pets-batch.csv
│   ├── orders-batch.txt
│   └── users-batch.csv
├── output/                    # Batch processing results (auto-created)
│   ├── results_20260215_143022.json
│   ├── results_20260215_143523.xlsx
│   └── results_20260215_143700.sqlite
├── .env                       # Configuration (copy from .env.example)
├── .env.example              # Configuration template
├── pyproject.toml            # Project metadata (uv/pip installable)
├── requirements.txt           # Python dependencies
└── README.md                 # Project documentation (from assets/README_template.md)
```

---

## File Descriptions

### `src/cli.py` — Main CLI Entry Point
**Purpose:** Root Click group that registers all resource commands

**Key Features:**
- Global options: `--config`, `--verbose`
- Subcommands for each API resource (pets, orders, users)
- Batch processing command for bulk requests
- Configuration loading and initialization

**Usage:**
```bash
uv run [cli-name] --help
uv run [cli-name] pets --help
uv run [cli-name] batch --help
```

---

### `src/client.py` — HTTP Client Library
**Purpose:** Wrapper around requests library for API calls

**Functionality:**
- Authentication setup (API Key, Bearer Token)
- HTTP methods: GET, POST, PUT, DELETE
- Error handling and response parsing
- Session management with connection pooling

**Usage:**
```python
from src.client import APIClient
from src.config import Config

client = APIClient(Config())
pets = client.get('/pet/findByStatus', {'status': 'available'})
```

---

### `src/config.py` — Configuration Management
**Purpose:** Load and manage settings from `.env` file

**Functionality:**
- Load environment variables from `.env`
- Get/set configuration values
- Save configuration changes
- Defaults and fallbacks

**Usage:**
```python
from src.config import Config

config = Config()
api_key = config.get('api_key')
config.set('log_level', 'DEBUG')
config.save()
```

---

### `src/batch_processor.py` — Batch Request Processor
**Purpose:** Process bulk requests from CSV/TXT files

**Functionality:**
- Parse CSV and TXT (JSON Lines) formats
- Execute requests sequentially
- Save results in JSON/CSV/XLSX/SQLite format
- Support timestamp in filenames
- Error handling and logging

**Usage:**
```bash
uv run [cli-name] batch \
  --input-file data/pets-batch.csv \
  --format json \
  --output-path ./output \
  --include-timestamp
```

---

### `src/logger.py` — Logging Helpers
**Purpose:** Provide a reusable logger setup for console/debug output.

### `src/output.py` — Output Helpers
**Purpose:** Shared helpers to export API payloads as JSON/CSV/XLSX/SQLite.

### `src/utils.py` — Utility Helpers
**Purpose:** Common parsing helpers (for example, safe parsing of `.env` values).

---

### `src/commands/{resource}_commands.py` — Resource Commands
**One file per API resource** (e.g., `pets_commands.py`, `users_commands.py`)

**Generated Commands per Resource:**
- `list` — List all resources
- `get` — Get specific resource by ID
- `create` — Create new resource
- `update` — Update existing resource (if applicable)
- `delete` — Delete resource (if applicable)

**Structure:**
```python
@click.group()
def pets_group():
    """Manage pets resources."""
    pass

@pets_group.command()
def list():
    """List all pets."""
    pass

@pets_group.command()
def get():
    """Get pet by ID."""
    pass
```

---

### `.env` — Configuration File
**Purpose:** Store sensitive configuration and settings

**Contents:**
```env
# API Connection
base_url=https://petstore.swagger.io/v2
api_key=your_api_key
api_token=your_bearer_token

# Output Configuration
output_format=json
timestamp_format=%Y%m%d_%H%M%S
include_timestamp=false

# Batch Processing
batch_input_format=csv
batch_output_path=./output

# Logging
log_level=INFO
verbose=false
```

**Note:** Always copy from `.env.example` and customize!

---

### `requirements.txt` — Python Dependencies
**Contents:**
```
click>=8.0.0
requests>=2.28.0
python-dotenv>=0.19.0
pandas>=1.3.0
openpyxl>=3.7.0
```

**Installation:**
```bash
pip install -r requirements.txt
```

---

### `tests/test_cli.py` — Smoke Tests
**Purpose:** Basic checks that root CLI and batch command help render successfully.

---

### `pyproject.toml` — Project Metadata
**Purpose:** Define package metadata, dependencies, and CLI entry point.

**Key Fields:**
- `[project]` name, version, description, Python requirement
- `dependencies` for runtime requirements
- `[project.scripts]` entry point for CLI command

**Usage:**
```bash
uv sync
uv run <project-name> --help
```

---

### `README.md` — Project Documentation

**Purpose:** Quick-start guide for users of the generated CLI project.

Generated from `assets/README_template.md` in the `prd-to-cli` skill. Each placeholder
is filled by running a specific command or reading a specific source after project generation:

| Placeholder | How to fill | Source |
|-------------|-------------|--------|
| `[PROJECT_NAME]` | User-provided project name | answered question |
| `[DESCRIPTION]` | One-line summary | PRD Introduction > Overview |
| `[BASE_URL]` | Base URL field | PRD `**Base URL:**` |
| `[REQUIRED_ENV_VARS]` | Required-only vars (no defaults) | read `.env.example` |
| `[CLI_HELP_OUTPUT]` | Root help text | `uv run [CLI_NAME] --help` |
| `[RESOURCE_HELP_SECTIONS]` | Per-resource help blocks | `uv run [CLI_NAME] [resource] --help` for each group |
| `[BATCH_DOCSTRING_EXAMPLES]` | Supported command examples | module docstring of `src/batch_processor.py` |
| `[TIMESTAMP_FORMAT]` | Timestamp pattern | Config.TIMESTAMP_FORMAT (e.g. `YYYYMMDD_HHMMSS`) |
| `[MAKE_HELP_OUTPUT]` | All Makefile targets | `make help` output |
| `[TREE_OUTPUT]` | Directory listing | `tree -a -I '__pycache__\|*.pyc\|uv.lock\|.env\|output\|logs\|.pytest_cache' --dirsfirst` |
| `[AUTH_HEADER]` | Auth header name | PRD Authentication section |
| `[PRD_FILENAME]` | PRD filename | basename of source PRD path |
| `[PRD_PATH]` | Relative path to PRD | relative path from project root to source PRD.md |

---

## Resource Commands Organization

Each API resource from the PRD becomes a Click command group with subcommands:

### Example: Pets Resource
```bash
# List all pets
uv run [cli-name] pets list

# Get pet by ID
uv run [cli-name] pets get --id 1

# Create new pet
uv run [cli-name] pets create --data '{"name": "Fluffy"}'

# Update pet
uv run [cli-name] pets update --id 1 --data '{"status": "sold"}'

# Delete pet
uv run [cli-name] pets delete --id 1
```

### Generated File: `src/commands/pets_commands.py`
```python
@click.group()
def pets_group(ctx):
    """Manage pets resources."""
    ctx.obj = ctx.obj or {}

@pets_group.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'xlsx']), default='json')
def list(format):
    """List all pets."""
    # Implementation

@pets_group.command()
@click.argument('id')
def get(id):
    """Get a pet by ID."""
    # Implementation

@pets_group.command()
@click.option('--data', type=str, help='JSON data')
def create(data):
    """Create a new pet."""
    # Implementation
```

---

## Data Directory

**Location:** `data/`
**Purpose:** Store input batch files (user-created)

**File Types:**
- `*.csv` — CSV format batch requests
- `*.txt` — JSON Lines format batch requests

**Example:** `data/pets-batch.csv`
```csv
method,endpoint,name,status
GET,/pet/findByStatus,available
POST,/pet,Fluffy,available
GET,/pet/1
```

---

## Output Directory

**Location:** `output/`
**Purpose:** Store batch processing results (auto-created)

**Generated Files:**
- `results.json` — Default results format
- `results_20260215_143022.json` — With timestamp
- `results.csv` — CSV export
- `results.xlsx` — Excel export
- `results.sqlite` — SQLite export with a `results` table

**Example:** `output/results.json`
```json
[
  {
    "method": "GET",
    "endpoint": "/pet/1",
    "status": 200,
    "data": {"id": 1, "name": "Fluffy"}
  }
]
```

---

## How Resources Map from PRD

The skill extracts API resources from your PRD.md based on section headers:

**PRD.md:**
```markdown
### PETS Resource
#### 1. List Pets
#### 2. Get Pet by ID
...

### ORDERS Resource
#### 1. Place Order
...

### USERS Resource
#### 1. Create User
...
```

**Generated Files:**
```
src/commands/pets_commands.py
src/commands/orders_commands.py
src/commands/users_commands.py
```

**CLI Structure:**
```
uv run [cli-name] pets list
uv run [cli-name] orders create
uv run [cli-name] users get
```

---

## Customization Points

After generation, you can customize:

1. **Add new commands** — Edit `src/commands/{resource}_commands.py`
2. **Enhance client** — Add methods to `src/client.py`
3. **Update config** — Modify `.env` settings
4. **Change defaults** — Edit `src/config.py` defaults
5. **Add validation** — Enhance parameter handling in commands

---

## Quick Start After Generation

```bash
# 1. Navigate to project
cd my_api_client

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API
cp .env.example .env
# Edit .env with your API key and settings

# 4. Test a command
uv run [cli-name] pets list

# 5. Process batch file
uv run [cli-name] batch \
  --input-file data/pets-batch.csv \
  --format json \
  --output-path output
```
