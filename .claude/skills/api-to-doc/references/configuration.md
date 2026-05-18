# Configuration & Customization

## Base URL Detection

The skill looks for base URL indicators in the fetched content:

- Meta tags: `<meta name="api-base-url" content="https://api.example.com">`
- Documentation text: `Base URL: https://api.example.com`
- JavaScript constants: `const API_BASE = "https://api.example.com"`

If not found, defaults to the domain of the provided URL.

### Manual Override

If base URL detection fails, manually edit the generated OpenAPI YAML file after successful extraction. Look for the `servers` section:

```yaml
servers:
  - url: https://api.example.com
    description: Production server
```

## Endpoint Tagging

Endpoints are automatically tagged by resource type (Users, Posts, Comments, etc.) based on the path structure. Tags help organize endpoints in the generated PRD and CLI project.

Example tags extracted from paths:
- `/users/*` → tag: `Users`
- `/posts/*` → tag: `Posts`
- `/comments/*` → tag: `Comments`

## Response Schemas

Generated responses use minimal but valid JSON schema:

```yaml
responses:
  '200':
    description: Successful response
    content:
      application/json:
        schema:
          type: object
          properties:
            data:
              type: object
```

Users can enhance these in the generated OpenAPI file or during the PRD generation step.

### Custom Schema Enhancement

For APIs with complex response structures, manually add property definitions to improve the generated PRD:

```yaml
schema:
  type: object
  properties:
    data:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
```
