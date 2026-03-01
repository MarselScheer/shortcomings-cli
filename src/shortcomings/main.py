from pathlib import Path

import typer
import yaml

app = typer.Typer(help="Shortcomings CLI")


@app.command()
def add_aspect(name: str, description: str):
    """Add a new aspect."""
    config_path = Path(".shortcomings.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)

    base_path = Path(config["base_path"])

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


if __name__ == "__main__":
    app()
