# api-to-doc Examples

## Example 1: Simple REST API

**Input URL:**
```
https://petstore.swagger.io/
```

**Auto-extracted information:**
- Base URL: `https://petstore.swagger.io`
- Endpoints detected:
  - GET /pet/findByStatus
  - GET /pet/{petId}
  - POST /pet
  - DELETE /pet/{petId}

**Generated OpenAPI (excerpt):**
```yaml
openapi: 3.0.0
info:
  title: Swagger Petstore
  version: 1.0.0
servers:
  - url: https://petstore.swagger.io
paths:
  /pet:
    post:
      summary: Add a new pet to the store
      tags:
        - Pet
      responses:
        '200':
          description: Successful response
  /pet/{petId}:
    get:
      summary: Find pet by ID
      tags:
        - Pet
      parameters:
        - name: petId
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Successful response
```

## Example 2: HTML Documentation with cURL Extraction

**Input URL:**
```
https://docs.example.com/api
```

**cURL command used internally:**
```bash
curl -s -L -A "Mozilla/5.0" https://docs.example.com/api
```

**HTML content snippet:**
```html
<h1>API Documentation</h1>
<p>Base URL: https://api.example.com/v1</p>

<h2>Users</h2>
<h3>List All Users</h3>
<code>GET /users</code>
<p>Returns paginated list of users</p>

<h3>Get User</h3>
<code>GET /users/{id}</code>
<p>Retrieve specific user by ID</p>

<h3>Create User</h3>
<code>POST /users</code>
<p>Create new user account</p>
```

**Extracted endpoints:**
```json
{
  "base_url": "https://api.example.com/v1",
  "title": "API Documentation",
  "endpoints": [
    {
      "method": "GET",
      "path": "/users",
      "description": "Returns paginated list of users",
      "tag": "Users"
    },
    {
      "method": "GET",
      "path": "/users/{id}",
      "description": "Retrieve specific user by ID",
      "tag": "Users"
    },
    {
      "method": "POST",
      "path": "/users",
      "description": "Create new user account",
      "tag": "Users"
    }
  ]
}
```

## Example 3: Interactive Fallback (When Auto-Detection Fails)

**Scenario:** User provides a URL with minimal API documentation.

**Skill behavior:**
1. Attempt to fetch and parse the URL
2. No endpoints found automatically
3. Fall back to interactive Q&A:

```
=== API Configuration ===

API Title: My Custom API
API Version: 2.1.0
Base URL: https://api.myapp.com
Description: Custom internal API

=== Define Endpoints ===

Endpoint 1:
  Method: GET
  Path: /products
  Description: List all products
  Tag: Products

Endpoint 2:
  Method: POST
  Path: /products
  Description: Create a new product
  Tag: Products

Endpoint 3:
  Method: GET
  Path: /products/{id}
  Description: Get specific product
  Tag: Products
```

**Generated OpenAPI:**
```yaml
openapi: 3.0.0
info:
  title: My Custom API
  version: 2.1.0
  description: Custom internal API
servers:
  - url: https://api.myapp.com
paths:
  /products:
    get:
      summary: List all products
      tags:
        - Products
      responses:
        '200':
          description: Successful response
    post:
      summary: Create a new product
      tags:
        - Products
      responses:
        '200':
          description: Successful response
  /products/{id}:
    get:
      summary: Get specific product
      tags:
        - Products
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful response
```

## Example 4: GitHub API (Complex Real-World Example)

**Input URL:**
```
https://api.github.com
```

**Auto-detected as:** Already in OpenAPI/spec format

**Output:** Direct conversion from GitHub's OpenAPI to our spec

**Resulting endpoints (sample):**
```
GET /repos/{owner}/{repo}
GET /repos/{owner}/{repo}/issues
POST /repos/{owner}/{repo}/issues
GET /repos/{owner}/{repo}/pulls
POST /repos/{owner}/{repo}/pulls
GET /repos/{owner}/{repo}/commits
```

## Workflow Example

### Step 1: Invoke the skill
```
/api-to-doc https://example-api.com/docs
```

### Step 2: Auto-detection
- Fetch URL with cURL
- Detect API type (OpenAPI spec, HTML docs, or unknown)
- Extract endpoints and base URL

### Step 3: Output
- Generate `openapi.yaml` in current directory
- Display extraction summary:
  ```
  ✅ API Documentation to OpenAPI Conversion
  📍 Base URL: https://api.example.com
  🔄 Detected 12 endpoints
  💾 Saved: openapi.yaml
  ```

### Step 4: Next Steps
```
Now use: /doc-to-prd @openapi.yaml
```

## Troubleshooting

### No endpoints detected

**Possible causes:**
- Website uses JavaScript to render content (cURL can't parse)
- Documentation is in unusual format
- Anti-bot protection prevents cURL access

**Solution:** Use interactive mode to manually define endpoints

### Partial endpoints extracted

**Possible causes:**
- Mixed documentation formats
- Non-standard HTTP method notation

**Solution:** Review extracted endpoints and use interactive mode to add missing ones

### Base URL not detected

**Possible causes:**
- Base URL in JavaScript or external config
- Multiple servers (dev/staging/prod)

**Solution:** Specify base URL in interactive step or edit generated YAML manually
