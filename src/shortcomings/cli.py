"""Shortcomings CLI - A command-line interface for managing project aspects, features, and shortcomings.

This module provides a Typer-based CLI for managing project aspects, features,
and shortcomings in a structured YAML format.
"""

import re
import json
from datetime import date
from importlib.metadata import version as get_version
from pathlib import Path
from typing import Literal

import typer
import yaml

from shortcomings.engine import (
    get_base_path,
    safe_load_yaml,
)

VALID_CRITICALITY_VALUES = {"low", "medium", "high", "critical"}
"""Set of valid criticality values for shortcomings."""


app = typer.Typer(help="Shortcomings CLI", add_completion=False)


@app.command()
def init():
    """Initialize a new .shortcomings.yaml configuration file."""
    config_file = Path(".shortcomings.yaml")
    if config_file.exists():
        typer.echo(f"Error: {config_file} already exists. Aborting.")
        raise typer.Exit(code=1)
    config_data = {"base_path": "."}
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
    typer.echo(f"Created {config_file}")


def _get_package_version() -> str:
    """Get the version of the installed package.

    Returns:
        str: The package version string, or "0.0.0" if it cannot be determined.
    """
    try:
        return get_version("shortcomings-cli")
    except Exception:
        return "0.0.0"


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", help="Show version", is_eager=True
    ),
):
    """Main callback for the Shortcomings CLI.

    Handles global options like --version and displays help when no subcommand
    is provided.

    Args:
        ctx: The Typer context.
        version: Whether to show the version information.
    """
    if version:
        typer.echo(_get_package_version())
        raise typer.Exit(code=0)

    # If no subcommand was invoked, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


def _validate_name(name: str):
    """Validate that name contains only alphanumeric characters, dashes, or underscores.

    Args:
        name: The string name to validate.

    Raises:
        typer.Exit: If the name contains invalid characters.
    """
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        typer.echo(
            f"Error: Invalid name '{name}'. Use only alphanumeric, dashes, or underscores.",
            err=True,
        )
        raise typer.Exit(code=1)


@app.command()
def add_aspect(name: str, user_story: str):
    """Add a new aspect to the project.

    Creates a new aspect directory with an aspect.yaml file containing the
    aspect name and user story.

    Args:
        name: The unique name for the aspect.
        user_story: The user story describing the aspect.

    Raises:
        typer.Exit: If an aspect with the given name already exists.
    """
    _validate_name(name)
    base_path = get_base_path()

    aspect_dir = base_path / "aspects" / name
    if aspect_dir.exists():
        typer.echo(f"Error: Aspect '{name}' already exists.", err=True)
        raise typer.Exit(code=1)

    aspect_dir.mkdir(parents=True, exist_ok=True)

    aspect_file = aspect_dir / "aspect.yaml"
    aspect_data = {
        "name": name,
        "user_story": user_story,
        "created_at": date.today().isoformat(),
    }
    with open(aspect_file, "w") as f:
        yaml.dump(aspect_data, f)

    typer.echo(f"Created aspect '{name}' at {aspect_file}")


@app.command()
def add_feature(
    aspect: str,
    name: str,
    description: str = "",
    tags: str = "",
):
    """Add a new feature to an aspect.

    Creates a new YAML file in the aspect's features directory.

    Args:
        aspect: The name of the aspect to add the feature to.
        name: The unique name for the feature.
        description: An optional description of the feature.
        tags: Comma-separated tags for the feature.

    Raises:
        typer.Exit: If the feature or aspect doesn't exist.
    """
    _validate_name(name)

    base_path = get_base_path()

    features_dir = base_path / "aspects" / aspect / "features"
    features_dir.mkdir(parents=True, exist_ok=True)

    tags_list = [t.strip() for t in tags.split(",")] if tags else []

    feature_file = features_dir / f"{name}.yaml"
    if feature_file.exists():
        typer.echo(
            f"Error: Feature '{name}' already exists in aspect '{aspect}'.", err=True
        )
        raise typer.Exit(code=1)

    feature_data = {
        "title": name,
        "description": description,
        "tags": tags_list,
        "created_at": date.today().isoformat(),
    }
    with open(feature_file, "w") as f:
        yaml.dump(feature_data, f)

    typer.echo(f"Created feature '{name}' at {feature_file}")


@app.command()
def add_shortcoming(
    aspect: str,
    name: str,
    description: str = "",
    criticality: Literal["low", "medium", "high", "critical"] = "critical",
    tags: str = "",
    depends_on: str = typer.Option(
        "us only",
        help="Describe if solving this shortcoming depends on others outside the developer team (e.g. stakeholders, other teams)",
    ),
):
    """Add a new shortcoming to an aspect.

    Creates a new YAML file in the aspect's shortcomings directory.

    Args:
        aspect: The name of the aspect to add the shortcoming to.
        name: The unique name for the shortcoming.
        description: An optional description of the shortcoming.
        criticality: The criticality level (low, medium, high, critical).
        tags: Comma-separated tags for the shortcoming.
        depends_on: Description of external dependencies for solving the shortcoming.

    Raises:
        typer.Exit: If the shortcoming already exists or criticality is invalid.
    """
    _validate_name(name)

    # Validate criticality
    if criticality and criticality.lower() not in VALID_CRITICALITY_VALUES:
        valid_values = ", ".join(sorted(VALID_CRITICALITY_VALUES))
        typer.echo(
            f"Error: Invalid criticality '{criticality}'. Must be one of: {valid_values}.",
            err=True,
        )
        raise typer.Exit(code=1)

    base_path = get_base_path()

    shortcomings_dir = base_path / "aspects" / aspect / "shortcomings"
    shortcomings_dir.mkdir(parents=True, exist_ok=True)

    tags_list = [t.strip() for t in tags.split(",")] if tags else []

    shortcoming_file = shortcomings_dir / f"{name}.yaml"
    if shortcoming_file.exists():
        typer.echo(
            f"Error: Shortcoming '{name}' already exists in aspect '{aspect}'.",
            err=True,
        )
        raise typer.Exit(code=1)

    shortcoming_data = {
        "title": name,
        "description": description,
        "criticality": criticality,
        "tags": tags_list,
        "depends_on": depends_on,
        "created_at": date.today().isoformat(),
    }
    with open(shortcoming_file, "w") as f:
        yaml.dump(shortcoming_data, f)

    typer.echo(f"Created shortcoming '{name}' at {shortcoming_file}")


def _get_aspects_dir() -> Path | None:
    """Get the aspects directory path, returning None if it doesn't exist.

    This is a convenience helper that combines get_base_path() with the
    aspects/ directory and checks for its existence.

    Returns:
        Path: The aspects directory path if it exists, None otherwise.
    """
    base_path = get_base_path()
    aspects_dir = base_path / "aspects"
    return aspects_dir if aspects_dir.exists() else None


@app.command(
    epilog="Tip: Use 'visidata' to explore the JSONL output: shortcomings list-all | vd"
)
def list_all():
    """List all aspects, features, and shortcomings in JSONL format.

    Iterates through all aspects in the aspects directory and prints each
    aspect, feature, and shortcoming as a JSON line to stdout.

    Output:
        Each line contains a JSON object with 'type' field indicating
        whether it's an aspect, feature, or shortcoming.
    """
    aspects_dir = _get_aspects_dir()
    if aspects_dir is None:
        return

    for aspect_path in aspects_dir.iterdir():
        aspect_file = aspect_path / "aspect.yaml"
        # Skip non-directories (stray files like README.md, .DS_Store) and
        # directories without aspect.yaml (incomplete/malformed aspects)
        if not aspect_file.exists():
            continue

        aspect_data = safe_load_yaml(aspect_file)
        aspect_data["type"] = "aspect"
        print(json.dumps(aspect_data))

        features_dir = aspect_path / "features"
        for feature_file in features_dir.glob("*.yaml"):
            feature_data = safe_load_yaml(feature_file)
            feature_data["type"] = "feature"
            feature_data["aspect"] = aspect_path.name
            print(json.dumps(feature_data))

        shortcomings_dir = aspect_path / "shortcomings"
        for shortcoming_file in shortcomings_dir.glob("*.yaml"):
            shortcoming_data = safe_load_yaml(shortcoming_file)
            shortcoming_data["type"] = "shortcoming"
            shortcoming_data["aspect"] = aspect_path.name
            print(json.dumps(shortcoming_data))


@app.command(epilog="Tip: Use 'visidata' to explore the JSONL output: shortcomings list-aspects | vd")
def list_aspects():
    aspects_dir = _get_aspects_dir()
    if aspects_dir is None:
        return

    for aspect_path in aspects_dir.iterdir():
        aspect_file = aspect_path / "aspect.yaml"
        if not aspect_file.exists():
            continue
        aspect_data = safe_load_yaml(aspect_file)
        aspect_data["type"] = "aspect"
        print(json.dumps(aspect_data))


@app.command()
def list_shortcomings(
    criticality: str | None = None,
):
    """List all shortcomings in JSONL format, optionally filtered by criticality.

    Iterates through all aspects and prints shortcomings as JSON lines.
    Can be filtered by criticality level if specified.

    Args:
        criticality: Optional filter to only show shortcomings of this criticality level.

    Output:
        Each line contains a JSON object representing a shortcoming,
        including 'type' and 'aspect' fields.
    """
    aspects_dir = _get_aspects_dir()
    if aspects_dir is None:
        return

    for aspect_path in aspects_dir.iterdir():
        shortcomings_dir = aspect_path / "shortcomings"
        for shortcoming_file in shortcomings_dir.glob("*.yaml"):
            shortcoming_data = safe_load_yaml(shortcoming_file)

            if (
                criticality is not None
                and shortcoming_data.get("criticality") != criticality
            ):
                continue

            shortcoming_data["type"] = "shortcoming"
            shortcoming_data["aspect"] = aspect_path.name
            print(json.dumps(shortcoming_data))
