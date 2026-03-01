"""Test for config file discovery."""
import pytest

from shortcomings.main import find_config_path


def test_find_config_path_in_current_dir(tmp_path, monkeypatch):
    """Test that config is found in the current working directory."""
    # Create a .shortcomings.yaml file in the current directory
    config_file = tmp_path / ".shortcomings.yaml"
    config_file.write_text("base_path: ./data")

    # Change to the temp directory
    monkeypatch.chdir(tmp_path)

    result = find_config_path()
    assert result == config_file


def test_find_config_path_in_parent_dir(tmp_path, monkeypatch):
    """Test that config is found in a parent directory."""
    # Create a nested directory structure
    config_file = tmp_path / ".shortcomings.yaml"
    config_file.write_text("base_path: ./data")

    nested_dir = tmp_path / "subdir" / "nested"
    nested_dir.mkdir(parents=True)

    # Change to the nested directory
    monkeypatch.chdir(nested_dir)

    result = find_config_path()
    assert result == config_file


def test_find_config_path_not_found(tmp_path, monkeypatch):
    """Test that an error is raised when config is not found."""
    # Change to a directory with no config file in any parent
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir(parents=True)

    monkeypatch.chdir(empty_dir)

    with pytest.raises(FileNotFoundError):
        find_config_path()
