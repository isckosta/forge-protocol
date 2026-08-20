from pathlib import Path

import typer
import yaml

from forge_cli.adapter_cli import adapter_app
from forge_cli.doctor import diagnose
from forge_cli.git import GitUnavailableError, NotGitRepositoryError, resolve_project_root
from forge_cli.migration import apply_migrations, find_candidates
from forge_cli.protocol_resources import resolve_protocol_root
from forge_cli.validation import validate_project
from forge_cli.version import CLI_VERSION, PROTOCOL_DISPLAY_VERSION, PROTOCOL_ID
from forge_cli.workspace import WorkspaceAlreadyInitializedError, initialize_workspace


INTERNAL_ERROR_EXIT_CODE = 70

app = typer.Typer()
app.add_typer(adapter_app, name="adapter")


def _protocol_root() -> Path:
    return resolve_protocol_root()


def _project_configuration(project_name: str) -> str:
    return yaml.safe_dump(
        {
            "schema": "forge/project@1",
            "project": {"name": project_name},
            "forge": {"protocol": PROTOCOL_ID},
            "flows": {
                "default": "standard",
                "allow_fast": True,
                "auto_escalation": True,
            },
            "testing": {"approach": "tdd_first"},
            "review": {"strict": True},
            "documentation": {"impact_evaluation": "required"},
        },
        sort_keys=False,
        allow_unicode=True,
    )


def _workspace_files(project_root: Path) -> dict[str, str]:
    return {
        "forge.yml": _project_configuration(project_root.name),
        "flows/fast.yml": "schema: forge/project-flow@1\nflow:\n  canonical: fast\n  enabled: true\n",
        "flows/standard.yml": "schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n",
        "flows/full.yml": "schema: forge/project-flow@1\nflow:\n  canonical: full\n  enabled: true\n",
    }


def _environment_git_unavailable() -> None:
    typer.echo("E_FORGE_GIT_UNAVAILABLE: Git executable is unavailable.")
    raise typer.Exit(code=3)


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
    typer.echo(f"Forge Protocol {PROTOCOL_DISPLAY_VERSION}")


@app.command()
def init() -> None:
    """Initialize Forge at the current Git repository root."""
    try:
        project_root = resolve_project_root(Path.cwd())
        initialize_workspace(project_root, _workspace_files(project_root))
    except GitUnavailableError:
        _environment_git_unavailable()
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
    except GitUnavailableError:
        _environment_git_unavailable()
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
def migrate(
    check: bool = typer.Option(
        False, "--check", help="Report migration candidates without applying them."
    ),
) -> None:
    """Migrate repository-native artifacts to their current schema shape.

    Recognizes exactly one schema family today:
    forge/execution-provenance@1 -> @2 (Contract C-075: never fabricates
    data; forge/change@1 and forge/adapter-installation@1 are out of
    scope for two different reasons -- see CHG-0019 discovery.md).
    """
    try:
        project_root = resolve_project_root(Path.cwd())
    except GitUnavailableError:
        _environment_git_unavailable()
    except NotGitRepositoryError:
        typer.echo("E_FORGE_NOT_GIT_REPOSITORY: current directory is not inside a Git repository.")
        raise typer.Exit(code=3)

    try:
        candidates = find_candidates(project_root)
        if check:
            if not candidates:
                typer.echo("No migration available.")
                return
            for candidate in candidates:
                typer.echo(
                    f"AVAILABLE {candidate.change_id}: {candidate.path} "
                    "-> forge/execution-provenance@2"
                )
            return

        results = apply_migrations(project_root, candidates)
    except Exception as error:
        _internal_error(error)

    if not results:
        typer.echo("Nothing to migrate.")
        return
    for result in results:
        typer.echo(
            f"MIGRATED {result.change_id}: {result.path} -> forge/execution-provenance@2"
        )


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
        "warning": "WARN",
    }
    for check in result.checks:
        typer.echo(f"{labels[check.status]} {check.id}: {check.message}")

    if not result.passed:
        raise typer.Exit(code=2)
