"""Tests for add-feature command."""

from pathlib import Path

from typer.testing import CliRunner

from shortcomings.main import app


def test_add_feature_creates_file():
    """Test that add-feature command creates the feature.yaml file."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create the config file
        config_path = Path(".shortcomings.yaml")
        config_path.write_text("base_path: .\n")

        # First, create an aspect (features belong to aspects)
        result = runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])
        assert result.exit_code == 0, f"Failed to create aspect: {result.output}"

        # Now add a feature to the aspect
        result = runner.invoke(
            app,
            [
                "add-feature",
                "ci",
                "github-actions",
                "--description",
                "GitHub Actions workflow for CI",
                "--tags",
                "ci,github,automation",
            ],
        )

        # Check if the command succeeded
        assert result.exit_code == 0, f"Command failed with: {result.output}"

        # Check if the file was created
        feature_file = Path("aspects") / "ci" / "features" / "github-actions.yaml"
        assert feature_file.exists(), f"File {feature_file} was not created"

        # Check the content of the file
        import yaml

        content = yaml.safe_load(feature_file.read_text())
        assert content["title"] == "github-actions"
        assert content["description"] == "GitHub Actions workflow for CI"
        assert content["tags"] == ["ci", "github", "automation"]
