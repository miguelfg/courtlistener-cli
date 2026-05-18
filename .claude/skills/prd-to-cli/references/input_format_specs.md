# Input Format Specifications

The skill accepts batch requests in two formats: CSV and TXT (JSON Lines).

## CSV Format

**File extension:** `.csv`
**Structure:** Standard CSV with headers in first row

### Example: pets-requests.csv
```
method,endpoint,name,status,photo_urls
GET,/pet/findByStatus,available
POST,/pet,,available,https://example.com/image.jpg
PUT,/pet/1,Fluffy,sold,
DELETE,/pet/1
```

**Requirements:**
- First row contains column headers
- Required columns: `method`, `endpoint`
- Optional columns depend on endpoint requirements
- HTTP methods: GET, POST, PUT, DELETE
- Endpoint paths start with `/`
- Data fields (name, status, etc.) populate request bodies

### CSV Example: orders-batch.csv
```
method,endpoint,pet_id,quantity,ship_date,status
POST,/store/order,1,2,2026-02-15,placed
POST,/store/order,5,1,2026-02-16,placed
GET,/store/order/1
DELETE,/store/order/2
```

---

## TXT Format (JSON Lines)

**File extension:** `.txt`
**Structure:** One JSON object per line (JSON Lines format)

### Example: users-requests.txt
```json
{"method": "POST", "endpoint": "/user", "username": "john_doe", "email": "john@example.com"}
{"method": "GET", "endpoint": "/user/john_doe"}
{"method": "PUT", "endpoint": "/user/john_doe", "email": "john.new@example.com"}
{"method": "DELETE", "endpoint": "/user/john_doe"}
```

**Requirements:**
- One JSON object per line
- Each object must have `method` and `endpoint` fields
- Additional fields become request body data
- No multi-line JSON objects
- Valid JSON syntax required

### TXT Example: pets-requests.txt
```json
{"method": "GET", "endpoint": "/pet/findByStatus", "status": "available"}
{"method": "POST", "endpoint": "/pet", "name": "Buddy", "photo_urls": "https://example.com/buddy.jpg", "status": "available"}
{"method": "GET", "endpoint": "/pet/1"}
{"method": "DELETE", "endpoint": "/pet/1"}
```

---

## Choosing the Right Format

| Use Case | Format | Reason |
|----------|--------|--------|
| Spreadsheet users | CSV | Easy to edit in Excel/Sheets |
| Programmatic generation | TXT (JSON Lines) | Each line is valid JSON |
| Simple requests | CSV | More readable for humans |
| Complex nested data | TXT (JSON Lines) | Better for complex structures |
| Large datasets | CSV | Native support in data tools |
| Streaming processing | TXT (JSON Lines) | Process line by line |

---

## Field Mapping to Request Body

When processing batch requests, the processor maps input fields to the API request:

### GET Requests
- Fields become query parameters
- Example CSV: `GET,/pet/findByStatus,available` becomes `/pet/findByStatus?status=available`

### POST/PUT Requests
- Fields (except `method` and `endpoint`) become JSON body
- Example CSV: `POST,/pet,Fluffy,available,https://example.com/pic.jpg` becomes:
```json
{
  "name": "Fluffy",
  "status": "available",
  "photo_urls": "https://example.com/pic.jpg"
}
```

### DELETE Requests
- URL path parameters extracted from endpoint
- No request body
- Example: `DELETE,/pet/123` deletes pet with ID 123

---

## Error Handling

**Missing Required Fields:**
- `method` or `endpoint` missing → Row skipped with error message
- Example: `,/pet` → "❌ Failed: Missing required field 'method'"

**Invalid Methods:**
- Must be one of: GET, POST, PUT, DELETE
- Example: `PATCH,/pet` → "❌ Failed: Unsupported HTTP method: PATCH"

**Malformed JSON (TXT only):**
- Each line must be valid JSON
- Example: `{method: "GET"}` → "❌ Failed: Invalid JSON on line 3"

**File Not Found:**
- Input file must exist and be readable
- Example: `--input-file missing.csv` → "Error: File not found: missing.csv"
