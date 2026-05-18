---
name: api-to-doc
description: Convert API documentation URLs into OpenAPI 3.0.0 YAML specs by auto-detecting API type, extracting endpoints with parameters/examples, and validating against the API. First step in the API-to-CLI workflow to generate the initial spec for doc-to-prd.
triggers:
  - User provides an API docs URL, API base URL, or Swagger/OpenAPI endpoint and wants an OpenAPI spec.
  - User asks to convert HTML API docs into an OpenAPI YAML file.
  - User is starting the API-to-CLI workflow and needs the first artifact (`<project-name>-api.yaml`).
do_not_trigger_when:
  mode: intent
  conditions:
    - Required input is missing (no API URL/docs URL/spec endpoint provided).
    - User intent is explanation, review, or discussion only (no artifact generation requested).
    - User already has a valid OpenAPI file and asks for a later pipeline step (PRD/CLI generation).
    - Request is ambiguous about target artifact and user has not confirmed intent.
---

# API to OpenAPI Generator

## Overview

The **api-to-doc** skill converts API URLs into standardized OpenAPI 3.0.0 YAML specifications. It intelligently fetches and parses API documentation from URLs, automatically extracts HTTP endpoints and metadata, and generates well-formed OpenAPI specs without manual boilerplate writing.

**Key features:**
- Auto-detect OpenAPI specs, Swagger, or HTML documentation
- Extract endpoints with complete parameter documentation (path, query, body parameters)
- Intelligently parse request/response examples from code blocks
- Extract parameter types and required/optional status
- Fallback to Playwright or WebFetch when cURL returns incomplete results
- HTML parsing with tag extraction and structure analysis
- Fail-fast when real documentation cannot be reliably retrieved/extracted
- Generate valid OpenAPI 3.0.0 YAML with enhanced schema information
- First step in the api-to-cli workflow

## Success Criteria

A skill execution is **successful** when:
- ✅ **≥ 5 unique endpoints** extracted from documentation
- ✅ **≥ 50% of probed GET endpoints** respond with 2xx/3xx HTTP status codes
- ✅ **Generated OpenAPI YAML** is syntactically valid and well-formed
- ✅ **All endpoints** have HTTP method (GET, POST, etc.) and path defined
- ✅ **Output file** created: `<project-name>-api.yaml` ready for `doc-to-prd` skill

A skill execution **fails** when:
- ❌ **Zero endpoints extracted** after auto-detection and multi-page crawling
- ❌ **All probed GET endpoints** return 404 (not found)
- ❌ **URL is unreachable** (network error, timeout, SSL failure)
- ❌ **Required input missing** (no API_URL provided)
- ❌ **No output file** generated (spec was invalid or incomplete)

## Input Requirements

When invoked, Claude receives:
- **API_URL** (required): A URL pointing to API documentation or an endpoint serving OpenAPI/Swagger spec
  - Examples: `https://petstore.swagger.io`, `https://api.github.com/docs`, `https://api.example.com`
- **OUTPUT_FOLDER** (optional): Directory where the generated `<project-name>-api.yaml` should be saved
  - Default: Current working directory

## How Claude Executes This Skill

### 1. Receive API URL

Claude receives the API documentation URL from the user. Examples:
- `https://example-api.com/docs`
- `https://petstore.swagger.io`

### 1.5. Script Execution Order

Execute the following scripts in sequence to convert the API URL to OpenAPI YAML:

**Primary script:** `scripts/fetch_api_info.py`
```bash
python scripts/fetch_api_info.py <API_URL>
```
This script:
- Fetches the documentation from the provided URL using cURL
- Auto-detects whether the content is an OpenAPI/Swagger spec, HTML docs, or Markdown
- Extracts HTTP endpoints, parameters, and examples using pattern matching
- Caches fetched HTML to `/tmp/api-to-doc-cache/` for inspection and debugging
- Outputs structured JSON with detected endpoints and metadata

If the primary extraction returns sparse results (few endpoints), execute the crawling script:

**Secondary script:** `scripts/crawler.py`
```bash
python scripts/crawler.py <API_URL> 10
```
This script:
- Discovers all API documentation pages across the same domain
- Extracts endpoints from all discovered pages
- Merges and deduplicates results

Finally, generate the OpenAPI YAML:

**Generation script:** `scripts/generate_openapi.py`
```bash
python scripts/generate_openapi.py <output-filename>.yaml <base_url> <endpoints_json>
```
This script:
- Creates a valid OpenAPI 3.0.0 YAML file
- Populates endpoints, parameters, and response schemas
- Validates endpoint normalization and existence

### 1.6. Fallback: Manual Configuration

If auto-detection fails completely and crawling yields no endpoints, the `scripts/interactive_flow.py` script provides interactive configuration:

```bash
python scripts/interactive_flow.py > api_config.json
```

This script prompts for:
- API title, version, description
- Base URL
- Manual endpoint definitions (method, path, description, tag)

**When to use:** Only after auto-detection and crawling have failed. Generates a minimal API configuration that can be used as input to `generate_openapi.py`.

**Note:** This is a last-resort fallback. The generated spec will be minimal and should be enhanced during the PRD generation step.

### 2. Auto-Detection

The skill attempts to:

1. **Fetch the URL** using cURL (handles redirects, follows links)
2. **Detect API type:**
   - If linked OpenAPI/Swagger JSON/YAML is discoverable → Extract directly (highest priority)
   - Else if markdown API docs are available → Parse markdown source (preferred over HTML)
   - Else if it's HTML documentation → Parse for HTTP endpoints
   - If unclear → Fail (do not fabricate endpoints)
3. **Extract endpoints** using regex patterns for common documentation formats
4. **Identify base URL** from content or request URL

### 3. Multi-Page Extraction and Fail-Fast Mode

For large docs portals, the skill automatically crawls related API docs pages (same root domain and API docs subtree) when top-level extraction is sparse, then merges and deduplicates endpoints before generation.

If auto-detection finds no real endpoints or retrieval is incomplete, the skill must fail with an explicit error and stop. Do not invent or manually fabricate endpoint definitions.

### 4. Generate OpenAPI YAML

Output a valid OpenAPI 3.0.0 file with:
- Info section (title, version, description)
- Server configuration
- All extracted endpoints with methods, paths, and tags
- Response definitions
- Parameter extraction (path variables, query params)

### 5. Quality Gates (Required)

Before finalizing the generated OpenAPI file, enforce these gates:

1. **Endpoint normalization gate**
   - Deduplicate `(method, path)` pairs
   - Ensure path formatting is valid and HTTP methods are valid

2. **GET endpoint existence gate**
   - Probe generated GET endpoints (without path template params) against the detected `base_url`
   - Treat HTTP `2xx/3xx` and compatibility responses (`400/401/403/405/406/409/415/422/429`) as endpoint existence signals
   - Filter out GET endpoints that fail existence checks (`404`/unreachable)

3. **Fail-fast gate**
   - If GET probes were attempted and none pass, fail generation instead of writing a misleading spec

4. **Report gate**
   - Include a quality report in the output spec under `x-quality-gates`

**Manual verification commands (recommended):**
```bash
# Check GET endpoints from generated OpenAPI YAML
python scripts/check_openapi_get_endpoints.py <project-name>-api.yaml

# Strict mode: fail if any probed GET endpoint fails
python scripts/check_openapi_get_endpoints.py <project-name>-api.yaml --fail-on-any-get-failure
```

**Direct curl spot-check examples:**
```bash
curl -s -L -o /dev/null -w "%{http_code}\n" "https://api.example.com/health"
curl -s -L -o /dev/null -w "%{http_code}\n" "https://api.example.com/v1/forecast"
```

## Execution Examples

### Example 0: Failed Extraction (Error Scenario)

**Input:** `https://internal-api.company.com/docs`

**Process:**
- Fetch documentation page
- Detect HTML but no endpoint patterns found
- Attempt multi-page crawling
- Still zero endpoints after crawling

**Outcome:** Exit with explicit error
```
ERROR: Could not extract any HTTP endpoints from https://internal-api.company.com/docs

Reasons this might happen:
- Documentation uses JavaScript rendering (cURL cannot execute JavaScript)
- API documentation in non-standard format or structure
- Anti-bot protection blocks automated requests

Remediation:
1. Verify the URL points to actual API documentation
2. If docs use JavaScript, use Playwright (webapp-testing skill) first
3. Try a direct OpenAPI/Swagger endpoint URL if available
4. Manually provide API endpoints via doc-to-prd step
```

**No output file generated.** User must either resolve the issue or provide alternative documentation.

### Example 1: Existing OpenAPI Spec

**Input:** `https://petstore.swagger.io`

**Process:** Detect Swagger specification and convert to OpenAPI 3.0.0 YAML

**Output:** `petstore-api.yaml` with all endpoints and schemas

### Example 2: HTML REST Documentation

**Input:** `https://api.github.com/docs`

**Process:** Parse HTML documentation, extract endpoints like:
- `GET /repos/{owner}/{repo}`
- `POST /repos/{owner}/{repo}/issues`
- `GET /repos/{owner}/{repo}/pulls`

**Output:** `github-api.yaml` with extracted endpoints and path parameters

### Example 3: Fail-Fast on Insufficient Docs

**Input:** `https://internal-api.company.com`

**Process:** Auto-detection finds no reliable endpoints

**Outcome:** Exit with explicit error message (do not generate misleading spec)

## Understanding the Output

Generated `<project-name>-api.yaml` structure:

```yaml
openapi: 3.0.0
info:
  title: API Title
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /users:
    get:
      summary: List users
      tags:
        - Users
      responses:
        '200':
          description: Successful response
  /users/{id}:
    get:
      summary: Get user by ID
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

The generated spec now includes:
- **Path Parameters**: Extracted from URL patterns (e.g., `{id}`, `:id`)
- **Query Parameters**: Parsed from documentation sections like "Query Parameters" or "Optional Parameters"
- **Request Body**: Extracted from "Request Body" sections or inferred from example JSON
- **Response Schemas**: Generated from "Response Example" sections when available
- **Parameter Types**: Inferred from documentation patterns (string, integer, object, etc.)
- **Required/Optional Status**: Detected from documentation language

For detailed OpenAPI structure reference, see [openapi_structure.md](references/openapi_structure.md).

## How API Detection Works

### Swagger/OpenAPI Detection

If the content contains `"openapi"` or `"swagger"` keys, it's treated as an existing spec and converted to OpenAPI 3.0.0.

### HTML Documentation Pattern Recognition

The skill searches for HTTP method + path patterns like:

```
GET /api/users
POST /users/{id}
DELETE /endpoint
```

Additionally, it extracts:
- **Path Parameters**: From `{id}`, `:id`, `[id]` patterns in URLs
- **Query Parameters**: From "Query Parameters" sections or inline patterns
- **Body Parameters**: From "Request Body" or "Payload" sections
- **Examples**: From code blocks marked "Request Example", "Response Example"

For detailed documentation patterns and extraction strategies, see [doc_patterns.md](references/doc_patterns.md).

### Fallback: MCP-Based Extraction (When cURL is Insufficient)

If cURL returns incomplete or empty results:
1. The skill notes this in the output
2. Recommendations are provided to use browser-based extraction
3. Consider using Playwright skill (webapp-testing) to render JavaScript-heavy docs
4. Or use WebFetch/WebSearch for additional context gathering

### Skill Integration: `wget-crawler` and `html-to-markdown-parser`

When raw retrieval is partial, blocked, or noisy, use these local skills as structured preprocessing:

1. **`wget-crawler` first** for static, multi-page documentation capture
   - Use it to mirror API docs sections locally when the user asks to crawl/clone/archive docs.
   - Prefer domain-limited, section-limited recursion and polite rate limits.
   - If mirrored pages are captured successfully, run extraction from the local mirror files.
2. **`html-to-markdown-parser` second** for cleanup and normalization
   - Use it on mirrored or cached HTML to remove navigation/ads/clutter and produce clean markdown.
   - Then run endpoint extraction against markdown-normalized content to improve method/path detection.
3. **Fail-fast still applies**
   - If these preprocessing steps still produce zero reliable endpoints, stop and return explicit failure.
   - Do not fabricate endpoints.

### Fail-Fast: No Fabricated Endpoints

If patterns don't match or endpoint extraction is empty/uncertain, stop with an error. Do not create guessed endpoints.

## Configuration & Customization

The skill automatically detects base URLs, tags endpoints by resource type, and generates response schemas. For detailed configuration options and customization, see [configuration.md](references/configuration.md).

## Next Steps in the Workflow

After generating `<project-name>-api.yaml`, the user should invoke the `doc-to-prd` skill with the generated OpenAPI file. This converts the OpenAPI spec into a comprehensive PRD.md with authentication, examples, and best practices—ready for the subsequent `prd-to-cli` skill.

## Troubleshooting

### No endpoints extracted

**Causes:**
- Website uses JavaScript rendering (cURL can't execute JS)
- Documentation in non-standard format
- Anti-bot protection blocks cURL

**Solutions:**
1. Skill will recommend browser-based extraction
2. Use Playwright (webapp-testing skill) to render the page first
3. Use WebFetch for alternative content fetching
4. Retry with a direct OpenAPI/Swagger URL if available
5. Use `wget-crawler` to capture a local static copy of docs, then parse locally
6. Use `html-to-markdown-parser` on captured HTML and retry extraction on cleaned markdown

### Incomplete parameter extraction

**Causes:**
- Parameters documented in images or diagrams
- Documentation uses non-standard terminology ("args", "fields", etc.)
- Parameters in external files or separate pages

**Solutions:**
1. Edit the generated OpenAPI YAML to add missing parameters
2. Use browser-based extraction for more complete access
3. Manually enhance parameters in the interactive PRD step

### Request/Response examples not extracted

**Causes:**
- Examples in JavaScript objects (not JSON)
- Examples in custom code block syntax
- Examples in HTML tables without code formatting

**Solutions:**
1. Examples can be added during the PRD generation step
2. Edit the OpenAPI spec to add `example` and `examples` properties
3. Consider providing raw API test examples in the PRD

### Base URL detection fails

**Causes:**
- Base URL in JavaScript or external config
- Multiple server environments (dev/staging/prod)

**Solution:** Edit the generated YAML manually after successful extraction

### Some endpoints missing

**Causes:**
- Documentation uses non-standard HTTP method notation
- Endpoints hidden behind expandable sections or tabs
- JavaScript-rendered navigation required

**Solutions:**
1. Add missing endpoints manually to generated YAML
2. Use browser-based extraction to access all documentation
3. Retry extraction from a more complete source URL

## Advanced Features

The skill includes advanced HTML parsing, intelligent parameter extraction, and automatic example/schema inference. For details on HTML content parsing, parameter extraction patterns, and example detection, see [advanced_features.md](references/advanced_features.md).

## HTML Caching & Crawling

The skill now includes advanced HTML management for comprehensive API documentation extraction:

### HTML Caching to `/tmp`

All fetched documentation pages are automatically saved to:
```
/tmp/api-to-doc-cache/
```

**Files are cached by default** to enable:
- Inspection and debugging of fetched content
- Link extraction for multi-page crawling
- Offline analysis of documentation
- Performance optimization for repeated requests

**Disable caching:**
```bash
python scripts/fetch_api_info.py <url> --no-cache
```

### HTML Cleanup and Markdown Conversion

When docs pages are very large/noisy, normalize them before analysis:

```bash
# Convert one HTML file to compact markdown
python scripts/html_to_markdown.py /tmp/api-to-doc-cache/<cached>.html /tmp/api-to-doc-cache/<cached>.md

# Batch-clean all cached HTML files and generate *.clean.html + *.md
python scripts/clean_cached_html.py /tmp/api-to-doc-cache
```

Use markdown-preferred extraction directly from the fetch step:

```bash
python scripts/fetch_api_info.py <url> --prefer-md-extraction --save-md-cache --md-max-lines 1200
```

### Link Extraction

The `link_extractor.py` helper identifies crawlable API documentation pages:

```bash
python scripts/link_extractor.py <html_file> <base_url> [output.json]
```

**Categorizes links into:**
- api_docs, endpoints, reference, guides, auth, examples, other

**Filters by:**
- Same domain only
- Excludes search, pagination, blogs, forums
- Path depth ≤ 2 levels by default

### Multi-Page Crawling

The `crawler.py` script discovers all API endpoints across multiple pages:

```bash
# Crawl up to 10 pages
python scripts/crawler.py <start_url>

# Crawl more pages
python scripts/crawler.py <start_url> 25 2
```

**Crawl workflow:**
1. Fetch page → Extract endpoints → Find links
2. Filter links → Queue crawlable pages
3. Repeat until max pages reached

**Output:** Complete list of endpoints discovered across entire documentation

### Optional Companion Workflow with Local Skills

For large or cluttered docs, chain local skills with the built-in scripts:

1. Use `wget-crawler` to download a bounded docs subtree to a local folder.
2. Use `html-to-markdown-parser` in batch mode on that folder.
3. Run extraction scripts against the mirrored/cached content to improve consistency.

This is especially useful when:
- Documentation is spread across many static HTML pages
- Navigation and boilerplate dominate page text
- Remote fetches are flaky but local copies are stable

For detailed crawling guide, see [crawling_guide.md](references/crawling_guide.md).

## References

- **[quick_reference.md](references/quick_reference.md)** — Script execution order flowchart, success criteria, and decision trees
- **[openapi_structure.md](references/openapi_structure.md)** — OpenAPI 3.0.0 schema and structure guide
- **[doc_patterns.md](references/doc_patterns.md)** — API documentation patterns and extraction strategies
- **[advanced_features.md](references/advanced_features.md)** — HTML parsing, parameter extraction, and example detection
- **[configuration.md](references/configuration.md)** — Base URL detection, endpoint tagging, and response schema customization
- **[error_handling.md](references/error_handling.md)** — Explicit fail conditions, error messages, and success thresholds
- **[crawling_guide.md](references/crawling_guide.md)** — HTML caching, link extraction, and multi-page crawling guide
- **[examples.md](references/examples.md)** — Real-world examples and workflow demonstrations

## Understanding the Generated OpenAPI Output

The skill generates OpenAPI 3.0.0 YAML files with the following structure (see `assets/openapi_template.yaml` for reference):

- **info**: API metadata (title, version, description, contact, license)
- **servers**: Base URL(s) where the API is hosted
- **paths**: HTTP endpoints with methods, parameters, request bodies, and responses
- **schemas**: Reusable type definitions for request/response validation

Reference template at `assets/openapi_template.yaml` shows:
- Standard endpoint definitions (GET, POST, PUT, DELETE)
- Path parameters (e.g., `{id}`)
- Request body schemas for POST/PUT
- Response codes and descriptions
- Tagging and summary documentation

Users can manually enhance the generated spec to add:
- Authentication schemes (OAuth2, API Key, etc.)
- More detailed schema properties
- Additional server environments (staging, development)
- Custom extensions under `x-*` keys

## Complete API-to-CLI Workflow

After generating the OpenAPI spec, the user continues with:

1. **Generate PRD**: User invokes `doc-to-prd` skill with the generated `<project-name>-api.yaml` to create a comprehensive PRD.md
2. **Generate CLI Project**: User invokes `prd-to-cli` skill with the PRD.md to generate a complete Python Click CLI project with batch processing and configuration management
