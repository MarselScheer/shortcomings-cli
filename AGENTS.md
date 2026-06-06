# Repo Structure

A UV managed repo. Key paths/files:

- `pyproject.toml` - Project metadata and dependencies
- `src/shortcomings/` - Source code directory
- `tests/` - Test suite
- `aspects/` - Aspects, features and shortcomings of the solution (`shortcomings --list-all` will also list everything from that folder)

# Core rules

- keep the AGENTS.md file updated, for instance if you create new development commands or modifies the repo structure
- keep the CHANGLOG.md file updated
- keep features under aspects/ updated

# CLI Commands

- `shortcomings init` - Initialize config
- `shortcomings add-aspect <name> <user_story>` - Add an aspect
- `shortcomings add-feature <aspect> <name>` - Add a feature to an aspect
- `shortcomings add-shortcoming <aspect> <name>` - Add a shortcoming to an aspect
- `shortcomings delete-shortcoming <name> [--aspect <aspect>]` - Delete a shortcoming by name (use --aspect if name is ambiguous)
- `shortcomings list-all` - List all aspects, features, and shortcomings
- `shortcomings list-aspects` - List aspects
- `shortcomings list-shortcomings` - List shortcomings

# Development Commands

Do NOT use `cd` before make targets; make handles directory context internally (e.g., use `make test` not `cd . && make test`)

- `make run` - Run the application
- `make test` - Run all tests
- `make coverage` - Runs tests and show line numbers of lines not covered
- `make test-file TEST_FILE=path/to/test.py` - Run a single test file
- `make lint` - Lint code with ruff
- `make format` - Format code with ruff
- `make fix` - Auto-fix lint issues
- `make typecheck` - Type check with ty
- `make check` - Run all checks (lint + typecheck)
- `uv run src/shortcomings/main.py [OPTIONS] COMMAND [ARGS]` - to use the shorcoming tool as defined by the current code base
