"""Consolidated tests for shortcomings CLI."""

import yaml
import pytest
from pathlib import Path
from typer.testing import CliRunner
from shortcomings.engine import find_config_path, get_base_path


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
