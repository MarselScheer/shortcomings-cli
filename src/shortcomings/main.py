import re
from pathlib import Path
from typing import Literal

import typer
import yaml

VALID_CRITICALITY_VALUES = {"low", "medium", "high", "critical"}


app = typer.Typer(help="Shortcomings CLI")


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
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return Path(config["base_path"])


def validate_name(name: str):
    """Validate that name contains only alphanumeric characters, dashes, or underscores."""
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        typer.echo(
            f"Error: Invalid name '{name}'. Use only alphanumeric, dashes, or underscores.",
            err=True,
        )
        raise typer.Exit(code=1)


@app.command()
def add_aspect(name: str, user_story: str):
    """Add a new aspect."""
    validate_name(name)
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
    """Add a new feature to an aspect."""
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
    depends_on: str = "",
):
    """Add a new shortcoming to an aspect."""
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
    }
    with open(shortcoming_file, "w") as f:
        yaml.dump(shortcoming_data, f)

    typer.echo(f"Created shortcoming '{name}' at {shortcoming_file}")


@app.command()
def list_all():
    """List all aspects, features and shortcomings in JSONL format."""
    import json

    base_path = get_base_path()
    aspects_dir = base_path / "aspects"

    # Guard: if aspects directory doesn't exist, return gracefully
    if not aspects_dir.exists():
        return

    for aspect_path in aspects_dir.iterdir():
        aspect_file = aspect_path / "aspect.yaml"
        with open(aspect_file) as f:
            aspect_data = yaml.safe_load(f)
        aspect_data["type"] = "aspect"
        print(json.dumps(aspect_data))

        features_dir = aspect_path / "features"
        for feature_file in features_dir.glob("*.yaml"):
            with open(feature_file) as f:
                feature_data = yaml.safe_load(f)
            feature_data["type"] = "feature"
            feature_data["aspect"] = aspect_path.name
            print(json.dumps(feature_data))

        shortcomings_dir = aspect_path / "shortcomings"
        for shortcoming_file in shortcomings_dir.glob("*.yaml"):
            with open(shortcoming_file) as f:
                shortcoming_data = yaml.safe_load(f)
            shortcoming_data["type"] = "shortcoming"
            shortcoming_data["aspect"] = aspect_path.name
            print(json.dumps(shortcoming_data))


if __name__ == "__main__":
    app()
