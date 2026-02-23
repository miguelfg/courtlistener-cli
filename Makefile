# CourtListener Python CLI - Development Makefile

.PHONY: install install-dev lint format test run help clean

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
	@echo "  make opinions-search-firearm-serial  Search opinions for \"serial number\" and \"firearm\""
	@echo "  make opinions-get     Example: Get single opinion"
	@echo "  make batch-example    Example: Batch processing"

install:
	uv sync

install-dev:
	uv pip install -e ".[dev]"

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

opinions-search-firearm-serial:
	uv run $(PROJECT_NAME) opinions list --search '"serial number" "firearm"' --limit 10 --format json

opinions-get:
	uv run $(PROJECT_NAME) opinions get 123456

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
