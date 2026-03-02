"""Tests for criticality validation."""

from pathlib import Path

from typer.testing import CliRunner

from shortcomings.main import app


def test_add_shortcoming_invalid_criticality_fails():
    """Test that adding a shortcoming with invalid criticality fails."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create the config file
        config_path = Path(".shortcomings.yaml")
        config_path.write_text("base_path: .\n")

        # Create an aspect (shortcomings belong to aspects)
        result = runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])
        assert result.exit_code == 0, f"Failed to create aspect: {result.output}"

        # Try to add a shortcoming with invalid criticality
        result = runner.invoke(
            app,
            [
                "add-shortcoming",
                "ci",
                "slow-builds",
                "--criticality",
                "very-high",  # Invalid - should be one of: low, medium, high, critical
            ],
        )

        # Command should fail with invalid criticality
        assert result.exit_code != 0, (
            f"Command should fail with invalid criticality 'very-high', but got exit_code=0. "
            f"Output: {result.output}"
        )
        # Error message should mention valid values
        assert "low" in result.output.lower() or "medium" in result.output.lower() or "high" in result.output.lower() or "critical" in result.output.lower() or "valid" in result.output.lower()
