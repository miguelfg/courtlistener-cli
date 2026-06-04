# CourtListener Python CLI - Development Makefile

.PHONY: install install-dev install-docs docs-build docs-serve lint format test run help clean search-slim-example docket-69717740 dockets-list docket-4134326-download-docs docket-4134326-parties

PROJECT_NAME = courtlistener-cli

# Load environment variables from .env when present.
ifneq (,$(wildcard .env))
include .env
export
endif

help:
	@echo "CourtListener Python CLI - Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make lint             Run code linting (ruff)"
	@echo "  make format           Format code (ruff)"
	@echo "  make test             Run tests"
	@echo ""
	@echo "Running:"
	@echo "  make run              Run CLI help"
	@echo "  make opinions-list    Example: List opinions"
	@echo "  make search-firearm-serial  Search all opinions for \"serial number\" and \"firearm\""
	@echo "  make search-firearm-serial-resume OFFSET=6820  Resume search from offset"
	@echo "  make search-firearm-serial-continue OFFSET=6820  Resume to part file by offset (no overwrite)"
	@echo "  make count-firearm-serial   Count search hits for \"serial number\" and \"firearm\""
	@echo "  make opinions-get     Example: Get single opinion"
	@echo "  make batch-example    Example: Batch processing"
	@echo "  make search-slim-example  Example: Search + slim export (key fields only)"
	@echo "  make docket-69717740      Fetch docket 69717740 and its entries"
	@echo "  make dockets-list                      Example: Batch dockets list from data/dockets.xlsx\n  make docket-4134326-download-docs      Download all free PDFs for docket 4134326 + manifest\n  make docket-4134326-parties            Get parties and criminal charges for docket 4134326"

install:
	uv sync

install-dev:
	uv pip install -e ".[dev]"

install-docs:
	uv pip install -e ".[docs]"

docs-build:
	uv run --extra docs mkdocs build

docs-serve:
	uv run --extra docs mkdocs serve

lint:
	-ruff check src/ tests/ --fix
	-ruff format src/ tests/

format:
	-ruff format src/ tests/

test:
	python3 -m pytest tests/ -v --tb=short

run:
	uv run $(PROJECT_NAME) --help

opinions-list:
	uv run $(PROJECT_NAME) opinions list --limit 10 --format json

search-firearm-serial:
	uv run $(PROJECT_NAME) search query --q '"serial number" "firearm"' --limit 0 --max-pages 0 --format xlsx --filename "firearm-with-serials"

search-firearm-serial-resume:
	uv run $(PROJECT_NAME) search query --q '"serial number" "firearm"' --offset $(if $(OFFSET),$(OFFSET),0) --limit 0 --max-pages 0 --format xlsx --filename "firearm-with-serials"

search-firearm-serial-continue:
	@if [ -z "$(OFFSET)" ]; then echo "Usage: make search-firearm-serial-continue OFFSET=<number>"; exit 1; fi
	uv run $(PROJECT_NAME) search query --q '"serial number" "firearm"' --offset $(OFFSET) --limit 0 --max-pages 0 --format xlsx --filename "firearm-with-serials_part_$(OFFSET)"

count-firearm-serial:
	uv run $(PROJECT_NAME) search count --q '"serial number" "firearm"' --type r

opinions-get:
	uv run $(PROJECT_NAME) opinions get 123456

docket-69717740:
	uv run $(PROJECT_NAME) search query --q "docket_id:69717740" --type r --limit 0 --max-pages 0 --format xlsx --filename docket_69717740 --slim

search-slim-example:
	uv run $(PROJECT_NAME) search query --q '"serial number" "firearm"' --limit 25 --format xlsx --slim

dockets-list:
	uv run $(PROJECT_NAME) dockets list data/dockets.xlsx --column docketNumber --limit 50 --max-pages 5 --format json

docket-4134326-download-docs:
	uv run $(PROJECT_NAME) dockets download-docs 4134326 --output ./output

docket-4134326-parties:
	uv run $(PROJECT_NAME) dockets parties 4134326 --output ./output

batch-example:
	@echo "Creating sample batch file..."
	@mkdir -p data
	@echo "method,endpoint,limit\nGET,/opinions/,20" > data/sample-batch.csv
	uv run $(PROJECT_NAME) batch --input-file data/sample-batch.csv --format json

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	find . -type f -name "*.pyc" -delete
	-rm -rf .pytest_cache
	-rm -rf .ruff_cache
