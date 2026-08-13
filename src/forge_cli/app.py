import typer


CLI_VERSION = "0.1.0.dev0"
PROTOCOL_VERSION = "1-draft"

app = typer.Typer()


@app.command()
def version() -> None:
    """Report Forge CLI and supported Protocol versions."""
    typer.echo(f"Forge CLI {CLI_VERSION}")
    typer.echo(f"Forge Protocol {PROTOCOL_VERSION}")
