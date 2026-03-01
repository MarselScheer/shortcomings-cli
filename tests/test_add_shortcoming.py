"""Tests for add-shortcoming command."""

from pathlib import Path

from typer.testing import CliRunner

from shortcomings.main import app


def test_add_shortcoming_creates_file():
    """Test that add-shortcoming command creates the shortcoming.yaml file."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create the config file
        config_path = Path(".shortcomings.yaml")
        config_path.write_text("base_path: .\n")

        # First, create an aspect (shortcomings belong to aspects)
        result = runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])
        assert result.exit_code == 0, f"Failed to create aspect: {result.output}"

        # Now add a shortcoming to the aspect
        result = runner.invoke(
            app,
            [
                "add-shortcoming",
                "ci",
                "slow-builds",
                "--description",
                "Builds take too long",
                "--criticality",
                "medium",
                "--tags",
                "performance,ci",
                "--depends-on",
                "self",
            ],
        )

        # Check if the command succeeded
        assert result.exit_code == 0, f"Command failed with: {result.output}"

        # Check if the file was created
        shortcoming_file = (
            Path("aspects") / "ci" / "shortcomings" / "slow-builds.yaml"
        )
        assert shortcoming_file.exists(), f"File {shortcoming_file} was not created"

        # Check the content of the file
        import yaml

        content = yaml.safe_load(shortcoming_file.read_text())
        assert content["title"] == "slow-builds"
        assert content["description"] == "Builds take too long"
        assert content["criticality"] == "medium"
        assert content["tags"] == ["performance", "ci"]
        assert content["depends_on"] == "self"


def test_add_shortcoming_fails_if_already_exists():
    """Test that adding a shortcoming that already exists fails."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create the config file
        config_path = Path(".shortcomings.yaml")
        config_path.write_text("base_path: .\n")

        # First, create an aspect
        result = runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])
        assert result.exit_code == 0, f"Failed to create aspect: {result.output}"

        # First add should succeed
        result1 = runner.invoke(app, ["add-shortcoming", "ci", "slow-builds"])
        assert result1.exit_code == 0, f"First add-shortcoming failed: {result1.output}"

        # Second add should fail
        result2 = runner.invoke(app, ["add-shortcoming", "ci", "slow-builds"])
        assert result2.exit_code != 0, "Adding duplicate shortcoming should fail"
        assert "already exists" in result2.output.lower()
