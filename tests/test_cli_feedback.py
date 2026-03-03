"""Tests for CLI feedback behavior."""
from typer.testing import CliRunner

from shortcomings.main import app


def test_cli_no_args_shows_help():
    """Running the CLI without arguments should display help."""
    runner = CliRunner()
    result = runner.invoke(app, [])

    # Help output should contain "Usage:"
    assert "Usage:" in result.output, f"Expected help output but got: {result.output!r}"
