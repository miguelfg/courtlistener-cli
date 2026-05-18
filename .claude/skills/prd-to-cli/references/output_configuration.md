# Output Configuration Reference

The skill generates a project with configurable output options for batch processing results.

## Output Formats

### JSON (Default)
- **Extension:** `.json`
- **Structure:** Array of result objects
- **Best for:** Scripting, piping to `jq`, structured data processing

```json
[
  {
    "method": "GET",
    "endpoint": "/pet/1",
    "status": 200,
    "data": {"id": 1, "name": "Fluffy", "status": "available"}
  },
  {
    "method": "POST",
    "endpoint": "/pet",
    "status": 201,
    "data": {"id": 2, "name": "Buddy"}
  }
]
```

### CSV
- **Extension:** `.csv`
- **Structure:** Flattened tabular format
- **Best for:** Spreadsheet analysis, data warehousing

```csv
method,endpoint,status,response_code,error
GET,/pet/1,success,200,
POST,/pet,success,201,
GET,/pet/999,error,404,Not found
```

### XLSX (Excel)
- **Extension:** `.xlsx`
- **Structure:** Multiple sheets by resource type
- **Best for:** Business users, data analysis, reporting

Sheets:
- `Summary` — Overview statistics
- `Pets` — Pet operation results
- `Orders` — Order operation results
- `Users` — User operation results

### SQLite
- **Extension:** `.sqlite`
- **Structure:** SQLite database file with a `results` table
- **Best for:** Repeatable local analysis, SQL queries, lightweight persistence

Example query:
```sql
SELECT * FROM results LIMIT 10;
```

---

## Configuration Options

### Output Path
**What:** Directory where results are saved
**Format:** Relative or absolute file path
**Default:** `./output`

**Examples:**
```bash
# Current directory
--output-path ./

# Specific directory
--output-path /tmp/results

# Nested directory (created automatically)
--output-path ./batch_results/2026_02_15
```

### Include Timestamp
**What:** Add timestamp to output filename
**Format:** Boolean flag
**Default:** False (no timestamp)

**With timestamp:**
```bash
# Results saved as: results_20260215_143022.json
--include-timestamp
```

**Without timestamp:**
```bash
# Results saved as: results.json
(no flag)
```

### Timestamp Format
**What:** Pattern for timestamp in filenames
**Options:**
- `YYYYMMDD_HHMMSS` — `20260215_143022`
- `YYYY-MM-DD_HH-MM-SS` — `2026-02-15_14-30-22`
- `ISO8601` — `2026-02-15T14:30:22Z`

**Set in `.env` file:**
```env
timestamp_format=%Y%m%d_%H%M%S
```

**Example filenames:**
```
results_20260215_143022.json       # YYYYMMDD_HHMMSS
results_2026-02-15_14-30-22.json   # YYYY-MM-DD_HH-MM-SS
results_2026-02-15T14:30:22Z.json  # ISO8601
```

---

## .env Configuration

**Location:** `.env` file in project root
**Template:** `.env.example` (copy and customize)

### Required Settings
```env
# API Connection
base_url=https://petstore.swagger.io/v2
api_key=special-key
api_token=your_bearer_token
```

### Output Settings
```env
# Output Configuration
output_format=json              # json, csv, xlsx, sqlite
timestamp_format=%Y%m%d_%H%M%S # Python strftime format
include_timestamp=false         # true or false
```

### Batch Processing
```env
# Batch Processing
batch_input_format=csv         # csv or txt
batch_output_path=./output     # Directory for results
```

### Logging
```env
# Logging
log_level=INFO                 # DEBUG, INFO, WARNING, ERROR
verbose=false                  # true or false
```

---

## Command-Line Usage

### Basic Batch Processing
```bash
# Process CSV file, output as JSON
uv run [cli-name] batch \
  --input-file pets-batch.csv \
  --format json \
  --output-path ./results

# Results: ./results/results.json
```

### With Timestamp
```bash
# Include timestamp in output filename
uv run [cli-name] batch \
  --input-file orders-batch.csv \
  --format json \
  --output-path ./batch_results \
  --include-timestamp

# Results: ./batch_results/results_20260215_143022.json
```

### Different Format
```bash
# Export to Excel
uv run [cli-name] batch \
  --input-file users-batch.txt \
  --format xlsx \
  --output-path ./exports

# Export to SQLite
uv run [cli-name] batch \
  --input-file users-batch.txt \
  --format sqlite \
  --output-path ./exports
```

### Verbose Output
```bash
# Show detailed processing information
uv run [cli-name] batch \
  --input-file pets-batch.csv \
  --verbose

# Output:
# [INFO] Loading batch file: pets-batch.csv
# [INFO] Parsed 5 requests
# ✅ Processed: GET /pet/findByStatus
# ✅ Processed: POST /pet
# ✅ Processed: GET /pet/1
# ...
```

---

## File Organization

```
project-name/
├── .env                    # Configuration (COPY from .env.example)
├── .env.example           # Configuration template
├── data/                  # Input files
│   ├── pets-batch.csv
│   ├── orders-batch.txt
│   └── users-batch.csv
└── output/                # Results (auto-created)
    ├── results_20260215_143022.json
    ├── results_20260215_143523.xlsx
    ├── results_20260215_143700.sqlite
    └── results_20260215_144012.csv
```

---

## Best Practices

### 1. Organize by Date
```bash
# Create dated output directories
--output-path ./results/$(date +%Y%m%d)
```

### 2. Include Descriptive Timestamps
```bash
# Makes it easy to identify when results were generated
--include-timestamp
```

### 3. Use Consistent Timestamp Format
Set in `.env` for all batch jobs:
```env
timestamp_format=%Y%m%d_%H%M%S
```

### 4. Archive Old Results
```bash
# Keep results, move old ones to archive
mv output/results_*.* archives/
```

### 5. Validate Input Before Processing
```bash
# Check file exists and is readable
uv run [cli-name] batch \
  --input-file data/batch.csv \
  --format json \
  --verbose
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Output path does not exist" | Directory not created | Use `--output-path ./output` (auto-created) |
| "Permission denied" | No write access to directory | Check file permissions, use different path |
| "Invalid timestamp format" | Malformed strftime pattern | Use valid Python strftime: `%Y%m%d_%H%M%S` |
| "No results saved" | Batch file had errors | Check input file format and errors in verbose output |
| "File already exists" | Filename collision | Use `--include-timestamp` to avoid overwrites |
