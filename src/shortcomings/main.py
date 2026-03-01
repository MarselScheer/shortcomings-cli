from pathlib import Path

import typer
import yaml

app = typer.Typer(help="Shortcomings CLI")


def get_base_path() -> Path:
    """Load base_path from .shortcomings.yaml config."""
    config_path = Path(".shortcomings.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return Path(config["base_path"])


@app.command()
def add_aspect(name: str, description: str):
    """Add a new aspect."""
    base_path = get_base_path()

    aspect_dir = base_path / "aspects" / name
    aspect_dir.mkdir(parents=True, exist_ok=True)

    aspect_file = aspect_dir / "aspect.yaml"
    aspect_data = {
        "name": name,
        "description": description,
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
    criticality: str = "",
    tags: str = "",
    depends_on: str = "",
):
    """Add a new shortcoming to an aspect."""
    base_path = get_base_path()

    shortcomings_dir = base_path / "aspects" / aspect / "shortcomings"
    shortcomings_dir.mkdir(parents=True, exist_ok=True)

    tags_list = [t.strip() for t in tags.split(",")] if tags else []

    shortcoming_file = shortcomings_dir / f"{name}.yaml"
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


if __name__ == "__main__":
    app()
