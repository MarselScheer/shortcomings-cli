import re
from importlib.metadata import version as get_version
from pathlib import Path

import typer
import yaml


def get_package_version() -> str:
    """Get the version of the installed package."""
    try:
        return get_version("shortcomings-cli")
    except Exception:
        return "0.0.0"


def safe_load_yaml(path: Path) -> dict:
    """Load and parse a YAML file, handling errors gracefully."""
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        typer.echo(f"Error: Invalid YAML in {path}: {e}", err=True)
        raise typer.Exit(code=1)


def find_config_path() -> Path:
    """Find .shortcomings.yaml by searching current and parent directories."""
    current = Path.cwd()
    for dir_path in [current] + list(current.parents):
        config_path = dir_path / ".shortcomings.yaml"
        if config_path.exists():
            return config_path
    raise FileNotFoundError(
        f"Config file .shortcomings.yaml not found in {current} or any parent directory"
    )


def get_base_path() -> Path:
    """Load base_path from .shortcomings.yaml config."""
    config_path = find_config_path()
    config = safe_load_yaml(config_path)
    return Path(config["base_path"])


def validate_name(name: str):
    """Validate that name contains only alphanumeric characters, dashes, or underscores."""
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        typer.echo(
            f"Error: Invalid name '{name}'. Use only alphanumeric, dashes, or underscores.",
            err=True,
        )
        raise typer.Exit(code=1)
