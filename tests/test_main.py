"""Consolidated tests for shortcomings CLI."""

import json
import yaml
import pytest
from pathlib import Path
from typer.testing import CliRunner
from shortcomings.main import app, find_config_path


class TestConfigDiscovery:
    """Tests for config file discovery."""

    def test_find_config_path_in_current_dir(self, tmp_path, monkeypatch):
        """Test that config is found in the current working directory."""
        config_file = tmp_path / ".shortcomings.yaml"
        config_file.write_text("base_path: ./data")
        monkeypatch.chdir(tmp_path)
        result = find_config_path()
        assert result == config_file

    def test_find_config_path_in_parent_dir(self, tmp_path, monkeypatch):
        """Test that config is found in a parent directory."""
        config_file = tmp_path / ".shortcomings.yaml"
        config_file.write_text("base_path: ./data")
        nested_dir = tmp_path / "subdir" / "nested"
        nested_dir.mkdir(parents=True)
        monkeypatch.chdir(nested_dir)
        result = find_config_path()
        assert result == config_file

    def test_find_config_path_not_found(self, tmp_path, monkeypatch):
        """Test that an error is raised when config is not found."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir(parents=True)
        monkeypatch.chdir(empty_dir)
        with pytest.raises(FileNotFoundError):
            find_config_path()


class TestAspectManagement:
    """Tests for add-aspect command."""

    def test_add_aspect_invalid_name_fails(self):
        """Test that adding an aspect with invalid name (e.g. spaces) fails."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            config_path = Path(".shortcomings.yaml")
            config_path.write_text("base_path: .\n")

            result = runner.invoke(app, ["add-aspect", "invalid name", "API endpoints"])
            assert result.exit_code != 0
            assert "invalid name" in result.output.lower()

    def test_add_aspect_creates_file(self):
        """Test that add-aspect command creates the aspect.yaml file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            config_path = Path(".shortcomings.yaml")
            config_path.write_text("base_path: .\n")

            result = runner.invoke(app, ["add-aspect", "api", "API endpoints"])
            assert result.exit_code == 0

            aspect_file = Path("aspects") / "api" / "aspect.yaml"
            assert aspect_file.exists()

            data = yaml.safe_load(aspect_file.read_text())
            assert data["name"] == "api"
            assert data["user_story"] == "API endpoints"

    def test_add_aspect_fails_if_already_exists(self):
        """Test that adding an aspect that already exists fails."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            config_path = Path(".shortcomings.yaml")
            config_path.write_text("base_path: .\n")

            runner.invoke(app, ["add-aspect", "api", "API endpoints"])
            result = runner.invoke(app, ["add-aspect", "api", "API endpoints"])
            assert result.exit_code != 0
            assert "already exists" in result.output.lower()


class TestFeatureManagement:
    """Tests for add-feature command."""

    def test_add_feature_creates_file(self):
        """Test that add-feature command creates the feature.yaml file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".shortcomings.yaml").write_text("base_path: .\n")
            runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])

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
            assert result.exit_code == 0

            feature_file = Path("aspects") / "ci" / "features" / "github-actions.yaml"
            assert feature_file.exists()

            content = yaml.safe_load(feature_file.read_text())
            assert content["title"] == "github-actions"
            assert content["description"] == "GitHub Actions workflow for CI"
            assert content["tags"] == ["ci", "github", "automation"]

    def test_add_feature_fails_if_already_exists(self):
        """Test that adding a feature that already exists fails."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".shortcomings.yaml").write_text("base_path: .\n")
            runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])
            runner.invoke(app, ["add-feature", "ci", "github-actions"])

            result = runner.invoke(app, ["add-feature", "ci", "github-actions"])
            assert result.exit_code != 0
            assert "already exists" in result.output.lower()


class TestShortcomingManagement:
    """Tests for add-shortcoming command and validation."""

    def test_add_shortcoming_creates_file(self):
        """Test that add-shortcoming command creates the shortcoming.yaml file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".shortcomings.yaml").write_text("base_path: .\n")
            runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])

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
            assert result.exit_code == 0

            sc_file = Path("aspects") / "ci" / "shortcomings" / "slow-builds.yaml"
            assert sc_file.exists()

            content = yaml.safe_load(sc_file.read_text())
            assert content["title"] == "slow-builds"
            assert content["criticality"] == "medium"
            assert content["tags"] == ["performance", "ci"]

    def test_add_shortcoming_fails_if_already_exists(self):
        """Test that adding a shortcoming that already exists fails."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".shortcomings.yaml").write_text("base_path: .\n")
            runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])
            runner.invoke(app, ["add-shortcoming", "ci", "slow-builds"])

            result = runner.invoke(app, ["add-shortcoming", "ci", "slow-builds"])
            assert result.exit_code != 0
            assert "already exists" in result.output.lower()

    def test_add_shortcoming_invalid_criticality_fails(self):
        """Test that adding a shortcoming with invalid criticality fails."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".shortcomings.yaml").write_text("base_path: .\n")
            runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])

            result = runner.invoke(
                app,
                ["add-shortcoming", "ci", "slow-builds", "--criticality", "very-high"],
            )
            assert result.exit_code != 0
            assert any(
                word in result.output.lower()
                for word in ["low", "medium", "high", "critical", "valid"]
            )


class TestListing:
    """Tests for list-all command."""

    def test_list_all_outputs_jsonl(self):
        """Test that list-all outputs entities in JSONL format."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".shortcomings.yaml").write_text("base_path: .\n")
            runner.invoke(app, ["add-aspect", "api", "API endpoints"])
            runner.invoke(app, ["add-feature", "api", "rest-api"])
            runner.invoke(app, ["add-shortcoming", "api", "no-auth"])

            result = runner.invoke(app, ["list-all"])
            assert result.exit_code == 0

            lines = result.output.strip().split("\n")
            assert len(lines) == 3
            for line in lines:
                obj = json.loads(line)
                assert obj["type"] in ["aspect", "feature", "shortcoming"]

    def test_list_all_handles_no_aspects(self):
        """Test that list-all handles the case when no aspects directory exists."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".shortcomings.yaml").write_text("base_path: .\n")
            result = runner.invoke(app, ["list-all"])
            assert result.exit_code == 0
            assert result.output.strip() == ""

    def test_list_all_handles_robustness(self):
        """Test robustness of list-all with missing subdirectories."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".shortcomings.yaml").write_text("base_path: .\n")
            runner.invoke(app, ["add-aspect", "test-aspect", "A test aspect"])

            # Aspect with no features
            result = runner.invoke(app, ["list-all"])
            assert result.exit_code == 0
            assert "test-aspect" in result.output

            # Aspect with feature but no shortcomings
            runner.invoke(app, ["add-feature", "test-aspect", "test-f"])
            result = runner.invoke(app, ["list-all"])
            assert result.exit_code == 0
            assert "test-f" in result.output


class TestListShortcomings:
    """Tests for list-shortcomings command."""

    def test_list_shortcomings_filters_by_criticality(self):
        """Test that list-shortcomings filters by criticality when provided."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".shortcomings.yaml").write_text("base_path: .\n")
            runner.invoke(app, ["add-aspect", "api", "API endpoints"])

            # Add shortcomings with different criticalities
            runner.invoke(
                app, ["add-shortcoming", "api", "sc1", "--criticality", "critical"]
            )
            runner.invoke(
                app, ["add-shortcoming", "api", "sc2", "--criticality", "high"]
            )
            runner.invoke(
                app, ["add-shortcoming", "api", "sc3", "--criticality", "medium"]
            )
            runner.invoke(
                app, ["add-shortcoming", "api", "sc4", "--criticality", "low"]
            )

            # Filter by 'critical'
            result = runner.invoke(
                app, ["list-shortcomings", "--criticality", "critical"]
            )
            assert result.exit_code == 0

            lines = [line for line in result.output.strip().split("\n") if line]
            assert len(lines) == 1
            obj = json.loads(lines[0])
            assert obj["title"] == "sc1"
            assert obj["criticality"] == "critical"
