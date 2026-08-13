from pathlib import Path

import typer

from forge_cli.git import NotGitRepositoryError, resolve_project_root
from forge_cli.validation import validate_project


CLI_VERSION = "0.1.0.dev0"
PROTOCOL_VERSION = "1-draft"

app = typer.Typer()


def _protocol_root() -> Path:
    return Path(__file__).resolve().parents[2] / "protocol"


@app.callback()
def main() -> None:
    """Forge CLI infrastructure commands."""


@app.command()
def version() -> None:
    """Report Forge CLI and supported Protocol versions."""
    typer.echo(f"Forge CLI {CLI_VERSION}")
    typer.echo(f"Forge Protocol {PROTOCOL_VERSION}")


@app.command()
def validate() -> None:
    """Validate the Forge project in the current Git repository."""
    try:
        project_root = resolve_project_root(Path.cwd())
    except NotGitRepositoryError:
        typer.echo("E_FORGE_NOT_GIT_REPOSITORY: current directory is not inside a Git repository.")
        raise typer.Exit(code=3)

    result = validate_project(project_root, _protocol_root())
    if result.passed:
        typer.echo("Forge project is valid")
        return

    for finding in result.findings:
        typer.echo(f"{finding.code} [{finding.artifact}] {finding.message}")

    raise typer.Exit(code=2)
