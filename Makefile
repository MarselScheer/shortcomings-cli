SHELL:=/bin/bash
.ONESHELL:

# ==============================================================================
# Testing
# ==============================================================================

test:
	@echo -------------------- $@ $$(date) --------------------
	uv run pytest

# Test a single test file (Usage: make test-file TEST_FILE=tests/test_storage.py)
test-file:
	@echo -------------------- test-file $$(date) --------------------
	uv run pytest $(TEST_FILE) -v

# ==============================================================================
# Code Quality
# ==============================================================================

lint:
	@echo -------------------- $@ $$(date) --------------------
	uv run ruff check .

format:
	@echo -------------------- $@ $$(date) --------------------
	uv run ruff format .

check: lint typecheck
	@echo -------------------- $@ $$(date) --------------------
	@echo All checks passed!

typecheck:
	@echo -------------------- $@ $$(date) --------------------
	uv run ty check

fix: format
	@echo -------------------- $@ $$(date) --------------------
	uv run ruff check --fix .

