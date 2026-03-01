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
        assert result.output.strip() == "", f"Expected empty output, got: {result.output}"
