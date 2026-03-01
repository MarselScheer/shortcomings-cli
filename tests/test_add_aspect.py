"""Tests for add-aspect command."""

from typer.testing import CliRunner
from pathlib import Path

from shortcomings.main import app


def test_add_aspect_creates_file():
    """Test that add-aspect command creates the aspect.yaml file."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create the config file
        config_path = Path(".shortcomings.yaml")
        config_path.write_text("base_path: .\n")

        result = runner.invoke(app, ["add-aspect", "api", "API endpoints"])

        # Check if the command succeeded
        assert result.exit_code == 0, f"Command failed with: {result.output}"

        # Check if the file was created
        aspect_file = Path("aspects") / "api" / "aspect.yaml"
        assert aspect_file.exists(), f"File {aspect_file} was not created"

        # Check the content of the file
        content = aspect_file.read_text()
        assert "api" in content
        assert "API endpoints" in content
