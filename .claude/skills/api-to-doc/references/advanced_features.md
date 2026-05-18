# Advanced Features

## HTML Content Parsing

The skill includes an `HTMLContentExtractor` class that:
- Parses HTML structure for better context understanding
- Extracts text content and code blocks separately
- Identifies section headers (h1-h5) for better organization
- Handles nested elements and preserves meaningful whitespace

This enables more accurate extraction of parameter documentation and examples.

## Parameter Extraction

### Path Parameters
Automatically extracted from endpoint URLs using patterns like `{id}`, `:id`, `[id]`

### Query Parameters
Located by searching for documentation sections containing:
- "Query Parameters"
- "Query String"
- "Optional Parameters"
- "Parameters"

### Request Body
Located by searching for sections containing:
- "Request Body"
- "Body Parameters"
- "Payload"
- "Body"

### Inferred from Examples
When explicit documentation is missing, types and required status are inferred from code examples.

## Example and Schema Extraction

The skill automatically extracts:
- **Request Examples**: From markdown/HTML code blocks labeled "Request Example"
- **Response Examples**: From code blocks labeled "Response Example"
- **Schema Generation**: Uses examples to infer field types and object structures
- **JSON Parsing**: Validates extracted examples as valid JSON before including
