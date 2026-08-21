"""JakeFSD command-line interface."""

import typer

app = typer.Typer(help="JakeFSD — local-first IDE for data pipelines")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo("JakeFSD 0.1.0")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show the JakeFSD version.",
    ),
) -> None:
    """JakeFSD CLI entry point."""


@app.command()
def version() -> None:
    """Show the JakeFSD version."""
    typer.echo("JakeFSD 0.1.0")


if __name__ == "__main__":
    app()
