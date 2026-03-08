"""Engine utilities for the shortcomings CLI.

This module provides core functionality for the shortcomings CLI, including
package version retrieval, configuration discovery, YAML parsing, and
input validation.

"""

from pathlib import Path

import typer
import yaml


def safe_load_yaml(path: Path) -> dict:
    """Load and parse a YAML file, handling errors gracefully.

    Args:
        path: The filesystem path to the YAML file.

    Returns:
        dict: The parsed YAML content.

    Raises:
        typer.Exit: If the YAML file is invalid or cannot be parsed.
    """
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        typer.echo(f"Error: Invalid YAML in {path}: {e}", err=True)
        raise typer.Exit(code=1)


def find_config_path() -> Path:
    """Find .shortcomings.yaml by searching current and parent directories.

    Returns:
        Path: The absolute path to the found configuration file.

    Raises:
        FileNotFoundError: If the config file is not found in the current or
            any parent directory.
    """
    current = Path.cwd()
    for dir_path in [current] + list(current.parents):
        config_path = dir_path / ".shortcomings.yaml"
        if config_path.exists():
            return config_path
    raise FileNotFoundError(
        f"Config file .shortcomings.yaml not found in {current} or any parent directory"
    )


def get_base_path() -> Path:
    """Load base_path from .shortcomings.yaml config.

    Returns:
        Path: The base path defined in the configuration.
    """
    config_path = find_config_path()
    config = safe_load_yaml(config_path)
    return Path(config["base_path"])
