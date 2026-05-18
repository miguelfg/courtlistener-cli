# Quick Reference: Script Execution Order

## Standard Workflow

```
INPUT: API_URL
   ↓
[1] python scripts/fetch_api_info.py <API_URL>
   ├─ Fetch documentation
   ├─ Auto-detect API type
   ├─ Extract endpoints
   └─ OUTPUT: endpoints.json
   ↓
[2] Check result
   ├─ If ≥ 5 endpoints found → Continue
   └─ If < 5 endpoints → [3a] Crawl
   ↓
[3] python scripts/generate_openapi.py <output>.yaml <base_url> <endpoints.json>
   ├─ Create OpenAPI 3.0.0 YAML
   ├─ Validate endpoints
   └─ OUTPUT: <project-name>-api.yaml
   ↓
OUTPUT: OpenAPI spec ready for doc-to-prd
```

## When Endpoints are Sparse (< 5 found)

```
[3a] python scripts/crawler.py <API_URL> 10
   ├─ Fetch multiple pages
   ├─ Extract all endpoints
   └─ Merge & deduplicate
   ↓
[3b] python scripts/generate_openapi.py <output>.yaml <base_url> <endpoints.json>
   └─ Continue with generation
```

## When Auto-Detection Fails (0 endpoints)

```
[4] Manual Configuration (Last Resort)

Option A: User provides alternative URL
   └─ Return to [1]

Option B: User accepts fallback config
   └─ python scripts/interactive_flow.py > api_config.json
   └─ python scripts/generate_openapi.py <output>.yaml <base_url> <api_config.json>

Option C: Fail - No spec generated
   └─ User must retry with different URL or skip to doc-to-prd step
```

## Quality Validation After Generation

```
[5] (Optional but recommended)
python scripts/check_openapi_get_endpoints.py <project-name>-api.yaml
   ├─ Probe GET endpoints
   ├─ Report quality metrics
   └─ --fail-on-any-get-failure flag: strict mode
```

## File Cache & Debugging

```
Fetched HTML files cached to: /tmp/api-to-doc-cache/

Inspect or convert cached files:
└─ python scripts/html_to_markdown.py <cached.html> <output.md>
└─ python scripts/clean_cached_html.py /tmp/api-to-doc-cache/
└─ python scripts/link_extractor.py <html_file> <base_url> [output.json]
```

## Success Criteria

✅ **Run is successful when:**
- ≥ 5 endpoints extracted
- ≥ 50% of probed GET endpoints respond with 2xx/3xx
- Generated OpenAPI YAML is syntactically valid
- All endpoints have method and path

❌ **Run fails when:**
- 0 endpoints extracted and crawling yields no results
- All probed endpoints return 404
- URL is unreachable
- Required API_URL parameter missing

## Next Steps

After successful generation, invoke:
```
/doc-to-prd @<project-name>-api.yaml
```

This converts the OpenAPI spec into a comprehensive PRD.md, ready for `prd-to-cli`.
