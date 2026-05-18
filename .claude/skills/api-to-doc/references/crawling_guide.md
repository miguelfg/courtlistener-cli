# API Documentation Crawling Guide

This guide explains the new crawling and link extraction features for the `api-to-doc` skill.

## Overview

The skill now includes three complementary tools for comprehensive API documentation extraction:

1. **HTML Caching** (`fetch_api_info.py`) - Saves fetched pages to `/tmp/api-to-doc-cache`
2. **Link Extraction** (`link_extractor.py`) - Extracts and categorizes links from documentation
3. **Multi-Page Crawling** (`crawler.py`) - Traverses multiple documentation pages
4. **HTML Cleanup + Markdown** (`clean_cached_html.py`, `html_to_markdown.py`) - Reduces noisy HTML and generates compact docs for easier parsing

## HTML Caching to /tmp

### Default Behavior

By default, when fetching API documentation, pages are automatically saved to:

```
/tmp/api-to-doc-cache/
```

Each page gets a unique filename based on:
- Domain name (URL-safe)
- Path component (truncated)
- URL hash (8 chars, for uniqueness)

Example filename:
```
api_example_com_v1_users_a1b2c3d4.html
```

### Cache Usage

**Check cache directory:**
```bash
ls -lah /tmp/api-to-doc-cache/
```

**View cached HTML:**
```bash
cat /tmp/api-to-doc-cache/api_example_com_docs_a1b2c3d4.html
```

**Disable caching for fresh fetch:**
```bash
python scripts/fetch_api_info.py <url> --no-cache
```

### Cache Benefits

- **Performance**: Subsequent requests for same URL use cached copy
- **Inspection**: Manually review fetched HTML for troubleshooting
- **Link Extraction**: Cached pages can be analyzed for crawlable links
- **Debugging**: Keep copies of documentation for analysis

### Convert Cached HTML to Cleaner Artifacts

```bash
# Batch process cache into /tmp/api-to-doc-cache/cleaned
python scripts/clean_cached_html.py /tmp/api-to-doc-cache

# Only markdown outputs, truncated for quick review
python scripts/clean_cached_html.py /tmp/api-to-doc-cache --skip-clean-html --max-lines 1200

# Convert one file manually
python scripts/html_to_markdown.py /tmp/api-to-doc-cache/<cached>.html /tmp/api-to-doc-cache/<cached>.md
```

You can also use markdown-preferred extraction during fetch:

```bash
python scripts/fetch_api_info.py <url> --prefer-md-extraction --save-md-cache --md-max-lines 1200
```

## Link Extraction

The `link_extractor.py` script analyzes HTML to find related API documentation pages.

### Basic Usage

```bash
# Extract links from cached HTML file
python scripts/link_extractor.py /tmp/api-to-doc-cache/api_example_com_docs_*.html https://api.example.com

# Extract from stdin
cat page.html | python scripts/link_extractor.py - https://api.example.com

# Save results to JSON
python scripts/link_extractor.py page.html https://api.example.com links.json
```

### Link Categorization

Links are automatically categorized into:

- **api_docs** - Core API documentation pages
- **endpoints** - Specific endpoint documentation
- **reference** - API reference material
- **guides** - Getting started and tutorial guides
- **auth** - Authentication and authorization pages
- **examples** - Code examples and samples
- **related_api** - Related APIs on other domains
- **other** - Uncategorized links

### Output Structure

```json
{
  "base_url": "https://api.example.com",
  "total_links": 145,
  "categorized": {
    "api_docs": 8,
    "endpoints": 12,
    "reference": 6,
    "guides": 4,
    "auth": 2,
    "examples": 5,
    "related_api": 0,
    "other": 102
  },
  "crawlable_count": 37,
  "crawlable_links": [
    {
      "url": "https://api.example.com/docs/endpoints/users",
      "href": "/docs/endpoints/users",
      "relative": true
    },
    ...
  ],
  "all_categorized": { ... }
}
```

### Understanding Crawlable Links

The script identifies "crawlable" links as:
- Same domain only
- Avoid search, pagination, blog, forums
- Path depth ≤ 2 levels from root
- Excludes archives, downloads, login pages
- Top 20 most relevant returned

## Multi-Page Crawling

The `crawler.py` script traverses multiple documentation pages to discover all endpoints.

### Basic Usage

```bash
# Crawl up to 10 pages with max depth 2
python scripts/crawler.py https://api.example.com/docs

# Crawl more pages
python scripts/crawler.py https://api.example.com/docs 25

# Limit path depth
python scripts/crawler.py https://api.example.com/docs 10 3
```

### How Crawling Works

1. **Start** at provided URL
2. **Extract** all endpoints from current page
3. **Find** all links on the page
4. **Filter** links to crawlable documentation pages
5. **Queue** new pages (up to 5 per page, max `max_pages` total)
6. **Repeat** until max pages reached

### Crawl Strategy

```
Start URL
  ↓
Fetch page 1 → Extract endpoints → Find links → Filter
  ↓ (add top 5 links to queue)
Fetch page 2 → Extract endpoints → Find links → Filter
  ↓
Fetch page 3 → ...
  ↓
Continue until max_pages reached
```

### Output Structure

```json
{
  "start_url": "https://api.example.com/docs",
  "base_domain": "api.example.com",
  "started_at": "2024-01-15T10:30:00",
  "pages_crawled": 10,
  "pages_visited": [
    "https://api.example.com/docs",
    "https://api.example.com/docs/endpoints/users",
    "https://api.example.com/docs/endpoints/posts",
    ...
  ],
  "total_endpoints": 42,
  "total_links_found": 450,
  "pages": [
    {
      "url": "https://api.example.com/docs",
      "status": "success",
      "content_length": 25000,
      "links_found": 120,
      "crawlable_links": 15,
      "endpoints": [
        { "method": "GET", "path": "/users" },
        { "method": "POST", "path": "/users" },
        ...
      ]
    },
    ...
  ]
}
```

## Workflow Examples

### Example 1: Single Page with Link Discovery

```bash
# Fetch main documentation page
python scripts/fetch_api_info.py https://api.example.com/docs

# Examine cached file
ls -la /tmp/api-to-doc-cache/

# Extract links from cached HTML
python scripts/link_extractor.py /tmp/api-to-doc-cache/api_example_com_docs_*.html \
  https://api.example.com links.json

# Review categorized links
cat links.json | jq '.categorized'

# Identify crawlable endpoints
cat links.json | jq '.crawlable_links'
```

### Example 2: Comprehensive Multi-Page Crawl

```bash
# Crawl documentation to discover all endpoints
python scripts/crawler.py https://api.example.com/docs 20 2 > crawl_results.json

# See summary
cat crawl_results.json | jq '{
  pages_crawled: .pages_crawled,
  endpoints_found: .total_endpoints,
  links_discovered: .total_links_found
}'

# Extract all unique endpoints
cat crawl_results.json | jq '.pages[].endpoints[] | {method, path}' | sort -u
```

### Example 3: Cache Inspection and Analysis

```bash
# List all cached files
ls -lh /tmp/api-to-doc-cache/

# Count total pages cached
ls /tmp/api-to-doc-cache/ | wc -l

# Search for specific patterns in cached pages
grep -l "Authentication" /tmp/api-to-doc-cache/*.html

# Extract all endpoints from all cached pages
for file in /tmp/api-to-doc-cache/*.html; do
  echo "=== $(basename $file) ==="
  grep -oP '(GET|POST|PUT|DELETE|PATCH)\s+/[^\s<]+' "$file"
done
```

### Example 4: Combining Crawl Results

```bash
# Crawl and save results
python scripts/crawler.py https://api.example.com/docs 15 > crawl.json

# Extract endpoints from crawl
cat crawl.json | jq -r '.pages[].endpoints[] | "\(.method) \(.path)"' | sort -u > endpoints.txt

# Generate feed to feed to prd-to-cli
cat endpoints.txt

# Manually enhance if needed
vim endpoints.txt

# Use in PRD generation
/prd-to-cli @endpoints.txt  # (in actual workflow)
```

## Cache Management

### Clear Cache

```bash
# Remove all cached pages
rm -rf /tmp/api-to-doc-cache/

# Or selective cleanup
rm /tmp/api-to-doc-cache/*_old.html
```

### Cache Size

```bash
# Check cache size
du -sh /tmp/api-to-doc-cache/

# Find largest files
ls -lhS /tmp/api-to-doc-cache/ | head
```

## Performance Considerations

### Default Behavior (Cached)

- **First run**: Full fetch + cache save (~2-5 seconds per page)
- **Subsequent runs**: Read from cache (~0.1 seconds)

### With --no-cache

- **Every run**: Full fetch, no caching (~2-5 seconds per page)

### Crawl Performance

- **10 pages**: ~20-50 seconds
- **20 pages**: ~40-100 seconds
- **50+ pages**: Consider reducing `max_depth` or filtering domains

### Recommendations

- Use caching for repeated analysis
- Use `--no-cache` only for fresh/updated documentation
- Limit crawl depth for faster execution
- Filter links to reduce queue size

## Troubleshooting

### Cache Directory Issues

**Problem**: Permission denied saving to `/tmp`

**Solution**: Use alternative directory

```bash
# Set custom cache directory (future enhancement)
export API_TO_DOC_CACHE="/home/user/api-docs-cache"
```

### Link Extraction Empty

**Problem**: No crawlable links found

**Causes**:
- Dynamic content (JavaScript-rendered)
- Links in JavaScript/external files
- Very deep path structure

**Solution**: Use Playwright for JavaScript-heavy docs

### Crawler Gets Stuck

**Problem**: Crawler hits same pages repeatedly

**Solution**:
- Reduce `max_depth` parameter
- Lower `max_pages` limit
- Check for redirect loops

### Cache Bloat

**Problem**: `/tmp/api-to-doc-cache/` grows too large

**Solution**:
- Regularly clean cache: `rm -rf /tmp/api-to-doc-cache/`
- Move cache to persistent location
- Implement cache expiration (future enhancement)

## Integration with Other Tools

### With Playwright

```bash
# Use Playwright for JS-heavy pages
# Then extract links
python scripts/link_extractor.py rendered_page.html <base_url>
```

### With WebFetch

```bash
# Fetch with WebFetch, then analyze
# Save output to HTML
# Run link extraction
python scripts/link_extractor.py fetched.html <base_url>
```

## Advanced: Custom Crawl Strategies

### Crawl All Pages

```bash
python scripts/crawler.py <url> 100 3
```

### Shallow Crawl (Fast)

```bash
python scripts/crawler.py <url> 5 1
```

### Deep Crawl (Comprehensive)

```bash
python scripts/crawler.py <url> 50 3
```

## Future Enhancements

Planned improvements:
- Custom cache location configuration
- Cache TTL (time-to-live) expiration
- Parallel page fetching
- Smart re-crawl detection
- Cache compression
- Link filtering by content type
- Endpoint deduplication across pages
