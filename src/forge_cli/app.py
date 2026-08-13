from pathlib import Path

import typer

from forge_cli.doctor import diagnose
from forge_cli.git import NotGitRepositoryError, resolve_project_root
from forge_cli.validation import validate_project
from forge_cli.workspace import WorkspaceAlreadyInitializedError, initialize_workspace


CLI_VERSION = "0.1.0.dev0"
PROTOCOL_VERSION = "1-draft"
INTERNAL_ERROR_EXIT_CODE = 70

app = typer.Typer()


def _protocol_root() -> Path:
    return Path(__file__).resolve().parents[2] / "protocol"


def _workspace_files(project_root: Path) -> dict[str, str]:
    project_name = project_root.name
    return {
        "forge.yml": (
            "schema: forge/project@1\n"
            "project:\n"
            f"  name: {project_name}\n"
            "forge:\n"
            "  protocol: 1\n"
            "flows:\n"
            "  default: standard\n"
            "  allow_fast: true\n"
            "  auto_escalation: true\n"
            "testing:\n"
            "  approach: tdd_first\n"
            "review:\n"
            "  strict: true\n"
            "documentation:\n"
            "  impact_evaluation: required\n"
        ),
        "flows/fast.yml": "schema: forge/project-flow@1\nflow:\n  canonical: fast\n  enabled: true\n",
        "flows/standard.yml": "schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n",
        "flows/full.yml": "schema: forge/project-flow@1\nflow:\n  canonical: full\n  enabled: true\n",
    }


def _internal_error(error: Exception) -> None:
    typer.echo(f"E_FORGE_INTERNAL_ERROR: {error}")
    raise typer.Exit(code=INTERNAL_ERROR_EXIT_CODE)


@app.callback()
def main() -> None:
    """Forge CLI infrastructure commands."""


@app.command()
def version() -> None:
    """Report Forge CLI and supported Protocol versions."""
    typer.echo(f"Forge CLI {CLI_VERSION}")
    typer.echo(f"Forge Protocol {PROTOCOL_VERSION}")


@app.command()
def init() -> None:
    """Initialize Forge at the current Git repository root."""
    try:
        project_root = resolve_project_root(Path.cwd())
        initialize_workspace(project_root, _workspace_files(project_root))
    except NotGitRepositoryError:
        typer.echo("E_FORGE_NOT_GIT_REPOSITORY: current directory is not inside a Git repository.")
        raise typer.Exit(code=3)
    except WorkspaceAlreadyInitializedError:
        typer.echo("E_FORGE_ALREADY_INITIALIZED: Forge is already initialized in this repository.")
        raise typer.Exit(code=2)
    except Exception as error:
        _internal_error(error)

    typer.echo(f"Forge initialized at {project_root / '.forge'}")


@app.command()
def validate() -> None:
    """Validate the Forge project in the current Git repository."""
    try:
        project_root = resolve_project_root(Path.cwd())
    except NotGitRepositoryError:
        typer.echo("E_FORGE_NOT_GIT_REPOSITORY: current directory is not inside a Git repository.")
        raise typer.Exit(code=3)

    try:
        result = validate_project(project_root, _protocol_root())
    except Exception as error:
        _internal_error(error)

    if result.passed:
        typer.echo("Forge project is valid")
        return

    for finding in result.findings:
        typer.echo(f"{finding.code} [{finding.artifact}] {finding.message}")

    raise typer.Exit(code=2)


@app.command()
def doctor() -> None:
    """Run read-only Forge environment and project diagnostics."""
    try:
        result = diagnose(Path.cwd(), _protocol_root())
    except Exception as error:
        _internal_error(error)

    labels = {
        "passed": "PASS",
        "failed": "FAIL",
        "skipped": "SKIP",
    }
    for check in result.checks:
        typer.echo(f"{labels[check.status]} {check.id}: {check.message}")

    if not result.passed:
        raise typer.Exit(code=2)
