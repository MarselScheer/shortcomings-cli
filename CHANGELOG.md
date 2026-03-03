# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.6] - 2026-03-03

### Added
- Help is now displayed when CLI is invoked without any subcommand.

## [0.0.5] - 2026-03-03

### Added
- `--version` flag to easily check the installed version of the CLI tool.
- Version is retrieved dynamically from package metadata.

## [0.0.4] - 2026-03-03

### Added
- Robust YAML loading with graceful error handling for corrupted or invalid YAML files.
- Clear error messages and exit code 1 when invalid YAML files are encountered.

### Changed
- Refactored `tests/test_main.py` to use pytest fixtures and helpers for cleaner test code.
- Improved CLI stability by handling `yaml.YAMLError` exceptions.

## [0.0.3] - 2026-03-03

### Added
- `list-shortcomings` command with criticality filtering support.
- Documentation for the aspects folder in AGENTS.md.

## [0.0.2] - 2026-03-02

### Added
- Name validation for aspects to ensure consistency.
- Initial aspect definitions and features for the core data model.
- Criticality validation and improved aspect creation logic.
- Recursive configuration file discovery for flexible setup.
- `list-all` command to output entities in JSONL format for better interoperability.
- Commands to manage `feature` and `shortcoming` entities.
- Core `aspect` management commands.
- Typer-based CLI with initial structure.
- Comprehensive `Makefile` for development tasks (test, lint, format, check).
- `AGENTS.md` documentation for repository structure and core rules.
- `CHANGELOG.md` added

### Fixed
- Improved code formatting and added robustness tests.
- Graceful handling of missing aspects directory.
- Prevention of duplicate additions for features and shortcomings.

### Changed
- Consolidated tests into a unified suite.

## [0.0.1] - 2026-03-01
- Initial project structure and basic CLI functionality.

---
🤖 Generated with [eca](https://eca.dev)
