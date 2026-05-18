# API Documentation Patterns

This guide covers common patterns the skill uses to extract API information from HTML documentation.

## Pattern Recognition

### HTTP Method + Path (Most Common)

**HTML Pattern:**
```html
<code>GET /api/users</code>
<h2>GET /api/users</h2>
<li>POST /api/users/{id}</li>
```

**Regex:** `(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s<\n]+)`

**Example extraction:**
```
GET /api/users      → method: GET, path: /api/users
POST /api/users/{id} → method: POST, path: /api/users/{id}
```

### Base URL Detection

**Common locations in HTML:**

1. In meta tags or headers:
```html
<meta name="api-base-url" content="https://api.example.com">
```

2. In documentation text:
```html
<p>Base URL: <code>https://api.example.com/v1</code></p>
```

3. In JavaScript/JSON:
```html
<script>const API_BASE = "https://api.example.com"</script>
```

**Regex patterns:**
- `base\s*(?:url|uri|endpoint)[\s:]*["\']?(https?://[^\s"\'<]+)`
- `api\s*endpoint[\s:]*["\']?(https?://[^\s"\'<]+)`
- `server[\s:]*["\']?(https?://[^\s"\'<]+)`

## Common API Documentation Structures

### Swagger/OpenAPI JSON

If the API already has an OpenAPI/Swagger spec:

```json
{
  "swagger": "2.0",
  "info": { "title": "API", "version": "1.0" },
  "paths": {
    "/users": {
      "get": { "summary": "List users" }
    }
  }
}
```

**Skill behavior:** Directly extract and convert to OpenAPI 3.0.

### REST API Documentation (HTML/Markdown)

**Typical structure:**
```
## Users Endpoints

### Get all users
GET /api/users

Returns a list of all users.

### Get specific user
GET /api/users/{id}

Retrieve a single user by ID.

### Create user
POST /api/users

Create a new user.
```

**Extraction logic:**
1. Identify HTTP method + path patterns
2. Extract surrounding context as description
3. Group by resource (Users, Posts, Comments, etc.)

### Endpoint Documentation Templates

#### Pattern: Method + Path + Description

```html
<h3>Create User</h3>
<code>POST /users</code>
<p>Create a new user account.</p>
```

#### Pattern: Table Format

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /users | List all users |
| POST | /users | Create user |
| GET | /users/{id} | Get user by ID |

#### Pattern: List Format

```
- GET /api/posts - Retrieve all posts
- POST /api/posts - Create a new post
- GET /api/posts/{id} - Get specific post
- PUT /api/posts/{id} - Update post
- DELETE /api/posts/{id} - Delete post
```

## Path Parameter Detection

Common path parameter patterns:

- `{id}` - Resource ID
- `{userId}` - Specific resource type ID
- `:id` - Alternative syntax
- `[id]` - Alternative syntax
- `$id` - Alternative syntax

**Normalized format:** Always convert to `{paramName}` format

## Query Parameter Documentation Patterns

The skill searches for these sections in endpoint documentation:

### Pattern 1: Explicit "Query Parameters" Section

**HTML:**
```html
<h4>Query Parameters</h4>
<ul>
  <li><code>page</code> - Page number (optional)</li>
  <li><code>limit</code> - Results per page (optional, default: 10)</li>
  <li><code>sort</code> - Sort field (optional)</li>
</ul>
```

**Extracted:** `page`, `limit`, `sort` as query parameters, all optional

### Pattern 2: Table Format

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number |
| limit | integer | No | Results per page |

**Extracted:** Parameters with types

### Pattern 3: Inline in Endpoint Description

**Text:**
```
GET /users?page=1&limit=10
Query Parameters: page (optional), limit (optional)
```

**Extracted:** Parameter names from the URL pattern

## Request/Response Examples (Enhanced Extraction)

The skill now extracts complete request and response examples from documentation to infer schemas.

### Pattern 1: Markdown Code Blocks (Most Common)

**HTML/Markdown:**
```markdown
### Create User

POST /api/users

**Request Example:**
\`\`\`json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user"
}
\`\`\`

**Response Example:**
\`\`\`json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "created_at": "2024-01-15T10:30:00Z"
}
\`\`\`
```

**Extracted:**
- Request: `name`, `email`, `role` as body parameters
- Response: `id`, `name`, `email`, `role`, `created_at` as response fields

### Pattern 2: HTML Pre/Code Blocks

**HTML:**
```html
<h4>Request</h4>
<pre><code>
{
  "username": "alice",
  "password": "secret123"
}
</code></pre>

<h4>Response</h4>
<pre><code>
{
  "token": "eyJ...",
  "expires_in": 3600
}
</code></pre>
```

**Extracted:** Parameters and response structure

### Pattern 3: Labeled Code Examples

**Text:**
```
Request:
POST /login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "pass123"
}

Response (200):
{
  "access_token": "...",
  "user": { "id": 1, "email": "user@example.com" }
}
```

**Extracted:** Request and response structures automatically

## Request Body Parameters (New)

Documentation sections describing POST/PUT/PATCH body fields:

### Pattern 1: Body Parameters Section

**HTML:**
```html
<h4>Request Body</h4>
<ul>
  <li><code>name</code> (string, required) - User full name</li>
  <li><code>email</code> (string, required) - User email address</li>
  <li><code>age</code> (integer, optional) - User age</li>
  <li><code>preferences</code> (object, optional) - User preferences</li>
</ul>
```

**Extracted:**
- `name` - type: string, required
- `email` - type: string, required
- `age` - type: integer, optional
- `preferences` - type: object, optional

### Pattern 2: Payload Documentation

**Text:**
```
POST /api/articles

**Payload:**
- title (required): Article title
- content (required): Article body
- tags (optional): Array of topic tags
- published (optional): Boolean, default false
```

**Extracted:** Field names and optional/required status

## Path Parameters (New)

Parameters extracted from URL patterns in endpoint definitions:

### Supported Formats

- `{id}` - Standard OpenAPI format
- `:id` - Express.js/Fastify format
- `[id]` - Alternative bracket format
- `$id` - Alternative dollar format

**Normalized to:** `{id}` in generated OpenAPI spec

**Example:**
```
GET /users/{userId}/posts/{postId}
Extracted: userId (path), postId (path)
```

## HTTP Status Codes

Common responses documented:

- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid auth
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Authentication Patterns

Look for these keywords:

- `API key`
- `Bearer token`
- `OAuth`
- `Basic auth`
- `Authorization header`
- `X-API-Key header`
- `API Key required`

**Common header patterns:**
- `Authorization: Bearer <token>`
- `Authorization: Basic <credentials>`
- `X-API-Key: <key>`
- `X-Auth-Token: <token>`

## Missing Information

When documentation is incomplete, the skill uses defaults:

- **Missing HTTP method:** Assume GET
- **Missing response type:** Assume JSON with generic object schema
- **Missing status codes:** Default to 200 for success, 400/500 for errors
- **Missing authentication:** Not included in spec (user provides via PRD)

## Example Extraction Workflow

Given this HTML:

```html
<h2>Users API</h2>
<p>Base URL: https://api.example.com/v2</p>

<h3>List Users</h3>
<code>GET /users?limit=10</code>
<p>Retrieve all users with pagination.</p>

<h3>Create User</h3>
<code>POST /users</code>
<p>Create a new user account.</p>

<h3>Get User</h3>
<code>GET /users/{id}</code>
<p>Get a specific user by ID.</p>
```

**Extracted endpoints:**
```json
{
  "title": "Users API",
  "base_url": "https://api.example.com/v2",
  "endpoints": [
    {
      "method": "GET",
      "path": "/users",
      "description": "Retrieve all users with pagination",
      "tag": "Users"
    },
    {
      "method": "POST",
      "path": "/users",
      "description": "Create a new user account",
      "tag": "Users"
    },
    {
      "method": "GET",
      "path": "/users/{id}",
      "description": "Get a specific user by ID",
      "tag": "Users"
    }
  ]
}
```
