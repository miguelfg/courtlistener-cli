.PHONY: help install install-dev lint format test run

PROJECT_NAME := {PROJECT_NAME_DASH}

help:
	@echo "{PROJECT_NAME_DASH} - Available commands"
	@echo ""
	@echo "  make install      Install dependencies with uv"
	@echo "  make install-dev  Install dependencies including dev extras"
	@echo "  make lint         Run basic lint checks"
	@echo "  make format       Format source code"
	@echo "  make test         Run tests"
	@echo "  make run          Show CLI help"
	@echo ""
	@echo "  CLI examples:"
{RESOURCE_HELP_LINES}

install:
	uv sync

install-dev:
	uv sync --all-extras

lint:
	uv run python -m py_compile src/*.py src/commands/*.py

format:
	uv run black src/
	uv run isort src/

test:
	uv run pytest tests/ -v

run:
	uv run $(PROJECT_NAME) --help

batch-example:
	uv run $(PROJECT_NAME) batch --input-file data/batch.csv --format json --output-path ./output

{RESOURCE_TARGETS}

.DEFAULT_GOAL := help
