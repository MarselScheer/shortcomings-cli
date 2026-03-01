"""Tests for list-all command."""

from pathlib import Path

from typer.testing import CliRunner

from shortcomings.main import app


def test_list_all_handles_no_aspects():
    """Test that list-all handles the case when no aspects directory exists."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create only the config file, no aspects directory
        config_path = Path(".shortcomings.yaml")
        config_path.write_text("base_path: .\n")

        # Run list-all command
        result = runner.invoke(app, ["list-all"])

        # Check if the command succeeded (didn't crash)
        assert result.exit_code == 0, f"Command failed with: {result.output}"

        # Should output empty (or at least not crash)
        assert result.output.strip() == "", (
            f"Expected empty output, got: {result.output}"
        )


def test_list_all_handles_aspect_with_no_features():
    """Test that list-all handles an aspect that has no features directory."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create config file
        config_path = Path(".shortcomings.yaml")
        config_path.write_text("base_path: .\n")

        # Use CLI to create an aspect (which creates the directory but no features)
        result = runner.invoke(app, ["add-aspect", "test-aspect", "A test aspect"])
        assert result.exit_code == 0, f"Failed to create aspect: {result.output}"

        # Run list-all command
        result = runner.invoke(app, ["list-all"])

        # Should not crash even if the aspect has no features
        assert result.exit_code == 0, f"Command failed with: {result.output}"

        # Should output the aspect
        assert "test-aspect" in result.output, (
            f"Expected aspect in output, got: {result.output}"
        )


def test_list_all_handles_aspect_with_no_shortcomings():
    """Test that list-all handles an aspect that has no shortcomings directory."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create config file
        config_path = Path(".shortcomings.yaml")
        config_path.write_text("base_path: .\n")

        # Use CLI to create an aspect (which creates the directory but no shortcomings)
        result = runner.invoke(app, ["add-aspect", "test-aspect", "A test aspect"])
        assert result.exit_code == 0, f"Failed to create aspect: {result.output}"

        # Add a feature to ensure the aspect has content
        result = runner.invoke(
            app,
            [
                "add-feature",
                "test-aspect",
                "test-feature",
                "--description",
                "A test feature",
            ],
        )
        assert result.exit_code == 0, f"Failed to create feature: {result.output}"

        # Run list-all command
        result = runner.invoke(app, ["list-all"])

        # Should not crash even if the aspect has no shortcomings
        assert result.exit_code == 0, f"Command failed with: {result.output}"

        # Should output the aspect and feature
        assert "test-aspect" in result.output, (
            f"Expected aspect in output, got: {result.output}"
        )
        assert "test-feature" in result.output, (
            f"Expected feature in output, got: {result.output}"
        )
