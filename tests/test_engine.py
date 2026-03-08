"""Consolidated tests for shortcomings CLI."""

import yaml
import pytest
from pathlib import Path
from typer.testing import CliRunner
from shortcomings.engine import find_config_path, get_base_path


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
