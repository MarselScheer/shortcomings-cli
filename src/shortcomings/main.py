import typer

app = typer.Typer(help="Shortcomings CLI")


@app.command()
def hello(name: str = "World"):
    """Say hello to someone."""
    typer.echo(f"Hello {name}!")


@app.command()
def goodbye(name: str = "World"):
    """Say goodbye to someone."""
    typer.echo(f"Goodbye {name}!")


if __name__ == "__main__":
    app()
