# ============================================================
# DataCo Web Scraper — Makefile
# ============================================================
# Usage:
#   make install     → Set up the full project environment
#   make run         → Run the scraper pipeline
#   make test        → Run all tests
#   make lint        → Check code quality
#   make format      → Auto-format all code
#   make clean       → Remove temporary files
# ============================================================

# Variables
PYTHON = .venv/bin/python
PIP = .venv/bin/pip
VENV = .venv

# ── Setup ────────────────────────────────────────────────────

## Create virtual environment, upgrade pip, and install dependencies
install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@echo "✅ Project environment ready."

# ── Run ──────────────────────────────────────────────────────

## Run the full scraping pipeline
run:
	$(PYTHON) -m src.dataco_web_scraper.pipeline
	@echo "✅ Pipeline complete."

# ── Testing ──────────────────────────────────────────────────

## Run all tests
test:
	$(PYTHON) -m pytest tests/ -v
	@echo "✅ All tests complete."

# ── Code Quality ─────────────────────────────────────────────

## Check code for style and quality issues
lint:
	$(PYTHON) -m ruff check src/ tests/
	@echo "✅ Lint check complete."

## Auto-format all code
format:
	$(PYTHON) -m ruff format src/ tests/
	@echo "✅ Code formatted."

# ── Cleanup ──────────────────────────────────────────────────

## Remove temporary files and caches
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "✅ Project cleaned."

# ── Help ─────────────────────────────────────────────────────

## Show all available commands
help:
	@echo ""
	@echo "DataCo Web Scraper — Available Commands"
	@echo "───────────────────────────────────────"
	@echo "  make install   → Set up the project environment"
	@echo "  make run       → Run the scraper pipeline"
	@echo "  make test      → Run all tests"
	@echo "  make lint      → Check code quality"
	@echo "  make format    → Auto-format all code"
	@echo "  make clean     → Remove temporary files"
	@echo ""

.PHONY: install run test lint format clean help