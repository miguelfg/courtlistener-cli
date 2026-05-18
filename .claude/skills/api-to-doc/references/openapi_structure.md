# OpenAPI 3.0.0 Structure

## Overview

OpenAPI 3.0.0 is the industry standard for describing REST APIs. This reference covers the essential structure for generating specifications from API documentation.

## Basic Structure

```yaml
openapi: "3.0.0"
info:
  title: API Title
  version: "1.0.0"
  description: Detailed description
  contact:
    name: Contact Name
    url: https://example.com
  license:
    name: MIT

servers:
  - url: https://api.example.com
    description: Production server
  - url: https://staging-api.example.com
    description: Staging server

paths:
  /users:
    get:
      summary: List users
      tags:
        - Users
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
```

## Key Sections

### `info` Object

Metadata about the API:

- `title` (required): Name of the API
- `version` (required): API version (semantic versioning recommended)
- `description`: Optional detailed description
- `contact`: Contact information
  - `name`: Contact name
  - `url`: Contact URL
  - `email`: Contact email
- `license`: License information
  - `name`: License name (MIT, Apache 2.0, etc.)
  - `url`: License URL

### `servers` Array

Server URLs where the API is available:

```yaml
servers:
  - url: https://api.example.com
    description: Production
  - url: https://staging.example.com
    description: Staging
```

### `paths` Object

All available API endpoints. Each path is a key, with HTTP methods as nested keys.

```yaml
paths:
  /resource:
    get:
      summary: Get resource
      responses: { ... }
    post:
      summary: Create resource
      responses: { ... }
  /resource/{id}:
    get:
      summary: Get specific resource
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses: { ... }
```

### `responses` Object

Possible responses for each method:

```yaml
responses:
  '200':
    description: Success
    content:
      application/json:
        schema:
          type: object
          properties:
            data:
              type: object
  '404':
    description: Not found
  '500':
    description: Server error
```

## Endpoint Definition

### Minimal Endpoint

```yaml
/users:
  get:
    summary: List users
    responses:
      '200':
        description: Success
        content:
          application/json:
            schema:
              type: object
```

### With Parameters

```yaml
/users/{id}:
  get:
    summary: Get user by ID
    parameters:
      - name: id
        in: path
        required: true
        schema:
          type: integer
      - name: include_posts
        in: query
        schema:
          type: boolean
    responses:
      '200':
        description: User object
```

### With Request Body

```yaml
/users:
  post:
    summary: Create user
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
              - email
            properties:
              name:
                type: string
              email:
                type: string
    responses:
      '201':
        description: Created
```

## Tags for Organization

Group endpoints by resource type:

```yaml
/users:
  get:
    tags:
      - Users
/posts:
  get:
    tags:
      - Posts
/users/{id}/posts:
  get:
    tags:
      - Users
      - Posts
```

## Common Patterns

### Standard HTTP Status Codes

- `200`: OK (GET, PUT, PATCH)
- `201`: Created (POST)
- `204`: No Content (DELETE)
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

### Media Types

- `application/json` - Most common
- `text/plain` - Plain text responses
- `text/csv` - CSV data
- `application/xml` - XML data
- `multipart/form-data` - File uploads

## Schema Types

```yaml
schema:
  type: object
  type: array
  type: string
  type: integer
  type: number
  type: boolean
  type: null
```
