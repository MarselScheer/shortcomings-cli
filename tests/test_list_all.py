"""Tests for list-all command."""

import json

from pathlib import Path

from typer.testing import CliRunner

from shortcomings.main import app


def test_list_all_outputs_jsonl():
    """Test that list-all outputs entities in JSONL format."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Create the config file
        config_path = Path(".shortcomings.yaml")
        config_path.write_text("base_path: .\n")

        # Create an aspect
        runner.invoke(app, ["add-aspect", "api", "API endpoints"])

        # Add a feature
        runner.invoke(
            app,
            [
                "add-feature",
                "api",
                "rest-api",
                "--description",
                "REST API endpoints",
                "--tags",
                "api,rest",
            ],
        )

        # Add a shortcoming
        runner.invoke(
            app,
            [
                "add-shortcoming",
                "api",
                "no-auth",
                "--description",
                "Missing authentication",
                "--criticality",
                "high",
            ],
        )

        # Run list-all command
        result = runner.invoke(app, ["list-all"])

        # Check if the command succeeded
        assert result.exit_code == 0, f"Command failed with: {result.output}"

        # Verify output is valid JSONL (one JSON object per line)
        lines = result.output.strip().split("\n")
        assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"

        # Verify each line is valid JSON with required fields
        for line in lines:
            obj = json.loads(line)
            assert "type" in obj, "Missing 'type' field"
            assert obj["type"] in ["aspect", "feature", "shortcoming"], f"Invalid type: {obj['type']}"