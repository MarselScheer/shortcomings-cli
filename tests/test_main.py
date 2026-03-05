class TestAddShortcomingHelpText:
    """Tests for add-shortcoming command help text."""

    def test_add_shortcoming_depends_on_help_text_mentions_external_dependencies(self):
        """Test that --depends-on help text explains it can include external dependencies."""
        runner = CliRunner()
        result = runner.invoke(app, ["add-shortcoming", "--help"])
        assert result.exit_code == 0

        # The help text should mention that depends_on can describe dependencies
        # on people outside the developer team
        assert "outside" in result.output.lower() or "others" in result.output.lower(), (
            "Help text for --depends-on should mention external/others dependencies"
        )
"""Consolidated tests for shortcomings CLI."""

import json
import yaml
import pytest
from pathlib import Path
from typer.testing import CliRunner
from shortcomings.main import app, find_config_path, get_base_path


# --- Fixtures & Helpers ---


@pytest.fixture
def cli_runner():
    """Fixture that provides an initialized CliRunner with config file."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path(".shortcomings.yaml").write_text("base_path: .\n")
        yield runner


def assert_yaml_content(file_path: Path, expected: dict):
    """Helper to verify YAML file content matches expected dict."""
    content = yaml.safe_load(file_path.read_text())
    for key, value in expected.items():
        assert content.get(key) == value, (
            f"Mismatch for key '{key}': {content.get(key)!r} != {value!r}"
        )


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

    def test_add_aspect_invalid_name_fails(self, cli_runner):
        """Test that adding an aspect with invalid name (e.g. spaces) fails."""
        result = cli_runner.invoke(app, ["add-aspect", "invalid name", "API endpoints"])
        assert result.exit_code != 0
        assert "invalid name" in result.output.lower()

    def test_add_aspect_creates_file(self, cli_runner):
        """Test that add-aspect command creates the aspect.yaml file."""
        result = cli_runner.invoke(app, ["add-aspect", "api", "API endpoints"])
        assert result.exit_code == 0

        aspect_file = Path("aspects") / "api" / "aspect.yaml"
        assert aspect_file.exists()
        assert_yaml_content(aspect_file, {"name": "api", "user_story": "API endpoints"})

    def test_add_aspect_fails_if_already_exists(self, cli_runner):
        """Test that adding an aspect that already exists fails."""
        cli_runner.invoke(app, ["add-aspect", "api", "API endpoints"])
        result = cli_runner.invoke(app, ["add-aspect", "api", "API endpoints"])
        assert result.exit_code != 0
        assert "already exists" in result.output.lower()


class TestFeatureManagement:
    """Tests for add-feature command."""

    def test_add_feature_creates_file(self, cli_runner):
        """Test that add-feature command creates the feature.yaml file."""
        cli_runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])

        result = cli_runner.invoke(
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
        assert_yaml_content(
            feature_file,
            {
                "title": "github-actions",
                "description": "GitHub Actions workflow for CI",
                "tags": ["ci", "github", "automation"],
            },
        )

    def test_add_feature_fails_if_already_exists(self, cli_runner):
        """Test that adding a feature that already exists fails."""
        cli_runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])
        cli_runner.invoke(app, ["add-feature", "ci", "github-actions"])

        result = cli_runner.invoke(app, ["add-feature", "ci", "github-actions"])
        assert result.exit_code != 0
        assert "already exists" in result.output.lower()


class TestShortcomingManagement:
    """Tests for add-shortcoming command and validation."""

    def test_add_shortcoming_creates_file(self, cli_runner):
        """Test that add-shortcoming command creates the shortcoming.yaml file."""
        cli_runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])

        result = cli_runner.invoke(
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
        assert_yaml_content(
            sc_file,
            {
                "title": "slow-builds",
                "criticality": "medium",
                "tags": ["performance", "ci"],
            },
        )

    def test_add_shortcoming_fails_if_already_exists(self, cli_runner):
        """Test that adding a shortcoming that already exists fails."""
        cli_runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])
        cli_runner.invoke(app, ["add-shortcoming", "ci", "slow-builds"])

        result = cli_runner.invoke(app, ["add-shortcoming", "ci", "slow-builds"])
        assert result.exit_code != 0
        assert "already exists" in result.output.lower()

    def test_add_shortcoming_invalid_criticality_fails(self, cli_runner):
        """Test that adding a shortcoming with invalid criticality fails."""
        cli_runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])

        result = cli_runner.invoke(
            app, ["add-shortcoming", "ci", "slow-builds", "--criticality", "very-high"]
        )
        assert result.exit_code != 0
        assert any(
            word in result.output.lower()
            for word in ["low", "medium", "high", "critical", "valid"]
        )

    def test_add_shortcoming_default_depends_on(self, cli_runner):
        """Test that depends_on defaults to 'us only' when not specified."""
        cli_runner.invoke(app, ["add-aspect", "ci", "CI pipeline"])

        result = cli_runner.invoke(
            app,
            [
                "add-shortcoming",
                "ci",
                "slow-builds",
                "--description",
                "Builds take too long",
            ],
        )
        assert result.exit_code == 0

        sc_file = Path("aspects") / "ci" / "shortcomings" / "slow-builds.yaml"
        assert sc_file.exists()
        assert_yaml_content(
            sc_file,
            {
                "depends_on": "us only",
            },
        )


class TestConfigRobustness:
    """Tests for robust YAML loading."""

    def test_config_corrupted_yaml_does_not_crash(self, tmp_path, monkeypatch):
        """Test that corrupted .shortcomings.yaml does not cause a traceback."""
        # Create a corrupted config file that will cause a YAML parse error
        config_file = tmp_path / ".shortcomings.yaml"
        # Invalid YAML: unclosed list
        config_file.write_text("base_path: [1,2,3")

        monkeypatch.chdir(tmp_path)

        # We expect the code to handle this gracefully - it should NOT raise yaml.YAMLError
        with pytest.raises(Exception) as exc_info:
            get_base_path()

        # The exception should NOT be a yaml.YAMLError (that's the fragile behavior)
        assert not isinstance(exc_info.value, yaml.YAMLError), (
            f"YAML loading raised yaml.YAMLError instead of handling gracefully: {exc_info.value}"
        )

    @pytest.mark.parametrize(
        "command,setup_func",
        [
            # (command, setup_func) where setup_func(config_dir, aspects_dir) -> None
            (
                ["list-all"],
                lambda cfg, asp: _create_aspect_with_invalid_yaml(
                    asp, "test-aspect", "aspect.yaml"
                ),
            ),
            (
                ["list-shortcomings"],
                lambda cfg, asp: _create_aspect_with_invalid_yaml(
                    asp,
                    "test-aspect",
                    "shortcomings/broken.yaml",
                    aspect_yaml_valid=True,
                ),
            ),
        ],
    )
    def test_handles_corrupted_yaml(self, tmp_path, monkeypatch, command, setup_func):
        """Parametrized test for corrupted YAML handling."""
        config_file = tmp_path / ".shortcomings.yaml"
        config_file.write_text("base_path: .\n")

        aspects_dir = tmp_path / "aspects"
        aspects_dir.mkdir()
        setup_func(tmp_path, aspects_dir)

        monkeypatch.chdir(tmp_path)

        runner = CliRunner()

        result = runner.invoke(app, command)
        if result.exception:
            assert not isinstance(result.exception, yaml.YAMLError), (
                f"{command} raised yaml.YAMLError instead of handling gracefully: {result.exception}"
            )


def _create_aspect_with_invalid_yaml(
    aspects_dir: Path,
    aspect_name: str,
    invalid_file_path: str,
    aspect_yaml_valid: bool = False,
):
    """Helper to create an aspect with invalid YAML in a specific file."""
    aspect_dir = aspects_dir / aspect_name
    aspect_dir.mkdir(parents=True, exist_ok=True)

    # Create aspect.yaml (valid or invalid based on flag)
    aspect_file = aspect_dir / "aspect.yaml"
    if aspect_yaml_valid:
        aspect_file.write_text(f"name: {aspect_name}\n")
    else:
        aspect_file.write_text("name: test\n  invalid: indentation")

    # Create the target file with invalid YAML
    target_file = aspect_dir / invalid_file_path
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text("title: broken\n  invalid: indentation")


class TestVersion:
    """Tests for --version flag."""

    def test_version_flag_outputs_version(self):
        """Test that --version flag outputs the package version."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        # Check that the output contains a version string (e.g., "0.0.5")
        assert "." in result.output  # Version contains dots


class TestListing:
    """Tests for list-all command."""

    def test_list_all_outputs_jsonl(self, cli_runner):
        """Test that list-all outputs entities in JSONL format."""
        cli_runner.invoke(app, ["add-aspect", "api", "API endpoints"])
        cli_runner.invoke(app, ["add-feature", "api", "rest-api"])
        cli_runner.invoke(app, ["add-shortcoming", "api", "no-auth"])

        result = cli_runner.invoke(app, ["list-all"])
        assert result.exit_code == 0

        lines = result.output.strip().split("\n")
        assert len(lines) == 3
        for line in lines:
            obj = json.loads(line)
            assert obj["type"] in ["aspect", "feature", "shortcoming"]

    def test_list_all_handles_no_aspects(self, cli_runner):
        """Test that list-all handles the case when no aspects directory exists."""
        result = cli_runner.invoke(app, ["list-all"])
        assert result.exit_code == 0
        assert result.output.strip() == ""

    def test_list_all_handles_robustness(self, cli_runner):
        """Test robustness of list-all with missing subdirectories."""
        cli_runner.invoke(app, ["add-aspect", "test-aspect", "A test aspect"])

        # Aspect with no features
        result = cli_runner.invoke(app, ["list-all"])
        assert result.exit_code == 0
        assert "test-aspect" in result.output

        # Aspect with feature but no shortcomings
        cli_runner.invoke(app, ["add-feature", "test-aspect", "test-f"])
        result = cli_runner.invoke(app, ["list-all"])
        assert result.exit_code == 0
        assert "test-f" in result.output


class TestRobustnessImplicitDirectoryStructure:
    """Tests for Implicit_Directory_Structure shortcoming.

    Ensures list-all and list-shortcomings handle malformed directories gracefully.
    """

    def test_list_all_handles_missing_aspect_yaml(self, cli_runner):
        """Test that list-all doesn't crash when aspect directory lacks aspect.yaml."""
        # Create aspects directory with a subdirectory that's missing aspect.yaml
        aspects_dir = Path("aspects")
        aspects_dir.mkdir()
        (aspects_dir / "incomplete-aspect").mkdir()

        # Also create a valid aspect for comparison
        cli_runner.invoke(app, ["add-aspect", "valid", "A valid aspect"])

        result = cli_runner.invoke(app, ["list-all"])

        # Should not crash - exit code 0
        assert result.exit_code == 0
        # Should still list the valid aspect
        assert "valid" in result.output

    def test_list_all_handles_stray_file_in_aspects(self, cli_runner):
        """Test that list-all doesn't crash when aspects/ contains a stray file."""
        # Create a valid aspect
        cli_runner.invoke(app, ["add-aspect", "api", "API endpoints"])

        # Create a stray file in aspects directory
        aspects_dir = Path("aspects")
        (aspects_dir / "README.md").write_text("# Aspects")

        result = cli_runner.invoke(app, ["list-all"])

        # Should not crash - exit code 0
        assert result.exit_code == 0
        # Should still list the valid aspect
        assert "api" in result.output

    def test_list_shortcomings_handles_missing_shortcomings_dir(self, cli_runner):
        """Test that list-shortcomings doesn't crash when aspect lacks shortcomings/ dir."""
        # Create a valid aspect but don't add any shortcomings
        cli_runner.invoke(app, ["add-aspect", "api", "API endpoints"])

        # Create another aspect directory without shortcomings folder
        aspects_dir = Path("aspects")
        (aspects_dir / "no-shortcomings").mkdir()
        (aspects_dir / "no-shortcomings" / "aspect.yaml").write_text("name: no-shortcomings\n")

        result = cli_runner.invoke(app, ["list-shortcomings"])

        # Should not crash - exit code 0
        assert result.exit_code == 0

    def test_list_shortcomings_handles_stray_file_in_aspects(self, cli_runner):
        """Test that list-shortcomings doesn't crash when aspects/ contains a stray file."""
        # Create a valid aspect
        cli_runner.invoke(app, ["add-aspect", "api", "API endpoints"])

        # Create a stray file in aspects directory
        aspects_dir = Path("aspects")
        (aspects_dir / "README.md").write_text("# Aspects")

        result = cli_runner.invoke(app, ["list-shortcomings"])

        # Should not crash - exit code 0
        assert result.exit_code == 0

    def test_list_shortcomings_handles_no_aspects_dir(self, cli_runner):
        """Test that list-shortcomings handles missing aspects directory gracefully."""
        # Don't create any aspects - aspects directory won't exist

        result = cli_runner.invoke(app, ["list-shortcomings"])

        # Should not crash - exit code 0
        assert result.exit_code == 0


class TestListShortcomings:
    """Tests for list-shortcomings command."""

    @pytest.mark.parametrize(
        "criticality,expected_title",
        [
            ("critical", "sc1"),
            ("high", "sc2"),
            ("medium", "sc3"),
            ("low", "sc4"),
        ],
    )
    def test_list_shortcomings_filters_by_criticality(
        self, cli_runner, criticality, expected_title
    ):
        """Test that list-shortcomings filters by criticality when provided."""
        cli_runner.invoke(app, ["add-aspect", "api", "API endpoints"])

        # Add shortcomings with different criticalities
        cli_runner.invoke(
            app, ["add-shortcoming", "api", "sc1", "--criticality", "critical"]
        )
        cli_runner.invoke(
            app, ["add-shortcoming", "api", "sc2", "--criticality", "high"]
        )
        cli_runner.invoke(
            app, ["add-shortcoming", "api", "sc3", "--criticality", "medium"]
        )
        cli_runner.invoke(
            app, ["add-shortcoming", "api", "sc4", "--criticality", "low"]
        )

        result = cli_runner.invoke(
            app, ["list-shortcomings", "--criticality", criticality]
        )
        assert result.exit_code == 0

        lines = [line for line in result.output.strip().split("\n") if line]
        assert len(lines) == 1
        obj = json.loads(lines[0])
        assert obj["title"] == expected_title
        assert obj["criticality"] == criticality
