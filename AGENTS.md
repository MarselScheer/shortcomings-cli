# Repo Structure

A UV managed repo. Key paths/files:

- None yet

# Core rules

- keep the AGENTS.md file updated, for instance if you create new development commands or modifies the repo structure

# Development Commands

Do NOT use `cd` before make targets; make handles directory context internally (e.g., use `make test` not `cd . && make test`)

- `make run` — Run the application
- `make test` — Run all tests
- `make test-file TEST_FILE=path/to/test.py` — Run a single test file
- `make lint` — Lint code with ruff
- `make format` — Format code with ruff
- `make fix` — Auto-fix lint issues
- `make typecheck` — Type check with ty
- `make check` — Run all checks (lint + typecheck)
