# Error Handling & Fail-Fast Conditions

## When to Exit with Error

The skill must exit with an explicit error message and **not generate any output** in the following situations:

### 1. No Endpoints Extracted

**Condition:** Auto-detection finds zero HTTP endpoints after fetching and parsing the provided URL.

**Error Message:**
```
ERROR: Could not extract any HTTP endpoints from {url}

Reasons this might happen:
- Documentation uses JavaScript rendering (cURL cannot execute JavaScript)
- API documentation in non-standard format or structure
- Anti-bot protection blocks automated requests
- Provided URL is not actual API documentation

Remediation:
1. Verify the URL points to actual API documentation
2. If docs use JavaScript, use Playwright (webapp-testing skill) first
3. Try a direct OpenAPI/Swagger endpoint URL if available
4. Manually provide API endpoints in doc-to-prd step
```

### 2. GET Endpoint Validation Fails (All Endpoints)

**Condition:** When probing GET endpoints from generated OpenAPI, all probed endpoints return 404 (not found) or are completely unreachable.

**Error Message:**
```
ERROR: Generated OpenAPI could not be validated against {base_url}

All probed GET endpoints returned 404 or were unreachable:
- GET {endpoint_1} → {http_code}
- GET {endpoint_2} → {http_code}
- ...

The extracted specification does not match the actual API.
Possible causes:
- Base URL auto-detection failed
- Extracted endpoints are incorrect/incomplete
- API has different routing structure than documentation

Remediation:
1. Manually verify base_url in generated YAML
2. Check if endpoint paths are correctly extracted
3. Re-try with URL to actual API documentation page
```

### 3. URL Fetch Fails

**Condition:** cURL cannot fetch the provided URL (timeout, DNS failure, SSL error, etc.).

**Error Message:**
```
ERROR: Could not fetch {url}

Network error or unreachable URL. Verify:
1. URL is publicly accessible
2. No firewall/proxy is blocking the request
3. URL is not rate-limiting automated requests
4. No SSL/certificate issues
```

### 4. Ambiguous or Missing Input

**Condition:** User does not provide a required API_URL parameter.

**Error Message:**
```
ERROR: API URL is required

Usage: Provide an API documentation URL or OpenAPI/Swagger endpoint

Examples:
- https://petstore.swagger.io
- https://api.example.com/docs
- https://api.github.com/openapi.json
```

## Do NOT Fabricate Endpoints

The skill **must never**:
- Guess or invent endpoints based on common patterns
- Assume endpoint names from API description text
- Extrapolate endpoints from partial documentation
- Generate endpoints from context clues if not explicitly found

**Example of What NOT to Do:**
```
❌ API docs mention "User Management API" → DON'T assume /users, /user/{id}, etc.
❌ Documentation shows one endpoint → DON'T invent other common REST endpoints
❌ API has 404 errors on probes → DON'T manually add them to the spec anyway
```

## Handling Incomplete Extractions

If extraction is sparse (fewer than 5 endpoints found):
1. Attempt multi-page crawling with `scripts/crawler.py`
2. If still sparse after crawling → **Fail** (do not generate incomplete spec)
3. If crawling succeeds with >5 endpoints → Continue to generation

## Quality Gate Failure Handling

If any quality gate fails:
- Endpoint Normalization: Log errors and clean the endpoint list
- GET Endpoint Probing: Filter out unreachable endpoints
- Fail-Fast Gate: **Stop and exit if no GET endpoints pass probes**
- Report Gate: Always include quality report in output spec under `x-quality-gates`

## Recommended Success Thresholds

Only consider the skill run successful if:
- ✅ Extracted ≥ 5 unique endpoints
- ✅ ≥ 50% of probed GET endpoints respond with 2xx/3xx
- ✅ Generated OpenAPI YAML is syntactically valid
- ✅ All endpoints have method and path

If any threshold is not met, provide error message with clear remediation steps.
