# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2026-03-08

### Added
- Name validation for `add-feature` and `add-shortcoming` commands - names cannot contain spaces or special characters (enforced via `validate_name()` function).
- `_get_aspects_dir()` helper in engine.py that combines base path lookup with existence check, returning `None` gracefully if directory doesn't exist.
- Unit tests for invalid name validation: `test_add_feature_invalid_name_fails` and `test_add_shortcoming_invalid_name_fails`.

### Changed
- Refactored `list-aspects`, `list-shortcomings`, and `list-all` commands to use the new `_get_aspects_dir()` helper for unified error handling.
- Consolidated two separate features into one: `Graceful_Missing_Dir` + `Robust_YAML_Loading` → `Robust_Aspect_Directory_And_YAML_Handling`.
- Improved test formatting by adding line breaks in multi-line assertions for better readability.

### Fixed
- Fixed naming inconsistency: shortcoming file `List Aspects Fragile YAML Handling.yaml` now uses underscores (`List_Aspects_Fragile_YAML_Handling.yaml`).

### Removed
- Removed feature `Graceful_Missing_Dir.yaml` (merged into `Robust_Aspect_Directory_And_YAML_Handling.yaml`).
- Removed feature `Robust_YAML_Loading.yaml` (merged into `Robust_Aspect_Directory_And_YAML_Handling.yaml`).

## [0.3.2] - 2026-03-07

### Fixed
- Graceful handling of missing `aspects/` directory in `list-aspects` command (previously crashed with `FileNotFoundError`, now returns empty output).

### Added
- New aspect `Graceful_Missing_Dir.yaml` to track the improved error handling.
- Unit test `test_list_aspects_handles_missing_aspects_dir` to prevent regressions.

### Removed
- Obsolete shortcoming `List Aspects Crashes On Missing Dir.yaml` (resolved by the fix above).
- Obsolete shortcoming `No_Init_Command.yaml` (functionality already implemented via the `init` command).

## [0.3.1] - 2026-03-07

### Fixed
- add missing created_at for feature `Safe_Init_Command`

### Removed
- clean up obsolete `Missing_Timestamps` shortcoming.

## [0.3.0] - 2026-03-07

### Added
- New `list-aspects` command to list all available aspects in JSONL format.

## [0.2.0] - 2026-03-06

### Added
- New `init` command to initialize the configuration file with default values.
- Protection against overwriting existing config files when running `init`.

## [0.1.0] - 2026-03-06

### Added
- `created_at` timestamp field automatically added to all YAML files (aspects, features, shortcomings).
- Tests for the `created_at` field and tool usage tracking.

## [0.0.10] - 2026-03-05

### Changed
- Refactored code into separate `cli` and `engine` modules for better organization.
- Added comprehensive docstrings to CLI and engine modules for improved documentation.

## [0.0.9] - 2026-03-05

### Added
- Support for "us only" dependency in aspects.

### Changed
- Set default `depends_on` to 'us only' in `add_shortcoming` command.
- Enhanced `add_shortcoming` help text for the `depends_on` field.
- Consolidated and improved CLI tests.

## [0.0.8] - 2026-03-05

### Added
- `Direct_YAML_Editing` feature in Lifecycle_Tracking: Users can directly edit YAML files in their preferred editor since the format is human-friendly. No complex edit command is needed.

### Removed
- `No_Edit_Command` shortcoming: Replaced with the `Direct_YAML_Editing` feature as a deliberate design decision.

## [0.0.7] - 2026-03-04

### Added
- Robust handling of malformed aspect directories in `list-all` and `list-shortcomings` commands.

### Fixed
- `list-all` no longer crashes when an aspect directory lacks `aspect.yaml`.
- `list-shortcomings` no longer crashes when the `aspects/` directory doesn't exist.
- Both commands now gracefully skip stray files (e.g., README.md, .DS_Store) in the aspects directory.

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
