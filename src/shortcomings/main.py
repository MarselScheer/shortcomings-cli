"""Main entry point for the Shortcomings CLI application.

This module serves as the executable entry point for the CLI.
It imports the Typer application from the cli module and runs it
when the module is executed directly (e.g., via `python -m shortcomings`).
"""

from shortcomings.cli import app

if __name__ == "__main__":
    app()
