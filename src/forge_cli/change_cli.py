"""Public CLI for creating repository-native Forge Change scaffolds."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
import yaml

from forge_cli.change_scaffolding import (
    ChangeRollbackIncompleteError,
    allocate_change_number,
    publish_scaffold,
    render_scaffold,
    validate_slug,
)
from forge_cli.configuration import (
    InvalidProjectConfigurationError,
    UnsupportedProtocolVersionError,
    load_project_configuration,
)
from forge_cli.git import GitUnavailableError, NotGitRepositoryError, resolve_project_root
from forge_cli.protocol_resources import resolve_protocol_root
from forge_cli.protocol_resolution import (
    InvalidProjectFlowConfigurationError,
    UnknownCanonicalFlowError,
    resolve_effective_flow,
)


DOMAIN_ERROR_EXIT_CODE = 2
ENVIRONMENT_ERROR_EXIT_CODE = 3
INTERNAL_ERROR_EXIT_CODE = 70

change_app = typer.Typer(help="Create repository-native Forge Change scaffolds.")


def _fail(code: str, message: str, exit_code: int = DOMAIN_ERROR_EXIT_CODE) -> None:
    typer.echo(f"{code}: {message}")
    raise typer.Exit(code=exit_code)


def _root() -> Path:
    try:
        return resolve_project_root(Path.cwd())
    except GitUnavailableError:
        _fail("E_FORGE_GIT_UNAVAILABLE", "Git executable is unavailable.", ENVIRONMENT_ERROR_EXIT_CODE)
    except NotGitRepositoryError:
        _fail("E_FORGE_NOT_GIT_REPOSITORY", "current directory is not inside a Git repository.", ENVIRONMENT_ERROR_EXIT_CODE)
    raise AssertionError("unreachable")


def _active_flow(root: Path) -> tuple[str, dict]:
    try:
        configuration = load_project_configuration(root / ".forge" / "forge.yml")
    except UnsupportedProtocolVersionError as error:
        _fail(error.code, str(error))
    except InvalidProjectConfigurationError as error:
        _fail(error.code, str(error))

    default = configuration["flows"]["default"]
    project_path = root / ".forge" / "flows" / f"{default}.yml"
    if not project_path.is_file():
        _fail("E_FORGE_INVALID_PROJECT_FLOW", f"Project Flow is missing: {project_path}.")
    try:
        project = yaml.safe_load(project_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as error:
        _fail("E_FORGE_INVALID_PROJECT_FLOW", str(error))
    if (
        not isinstance(project, dict)
        or project.get("schema") != "forge/project-flow@1"
        or not isinstance(project.get("flow"), dict)
        or project["flow"].get("enabled") is not True
        or not isinstance(project["flow"].get("canonical"), str)
    ):
        _fail("E_FORGE_INVALID_PROJECT_FLOW", f"Project Flow is invalid or disabled: {project_path}.")
    try:
        effective = resolve_effective_flow(
            resolve_protocol_root(), root, default, configuration["forge"]["protocol"]
        )
    except UnknownCanonicalFlowError as error:
        _fail("E_FORGE_UNKNOWN_CANONICAL_FLOW", str(error))
    except (InvalidProjectFlowConfigurationError, OSError) as error:
        _fail("E_FORGE_INVALID_PROJECT_FLOW", str(error))
    return effective["canonical"]["flow"]["id"], effective["canonical"]


@change_app.command("new")
def new_change(
    slug: Annotated[str, typer.Argument(metavar="SLUG")],
    non_behavioral: Annotated[bool, typer.Option("--non-behavioral")] = False,
) -> None:
    """Plan and create a new repository-native Change scaffold."""
    root = _root()
    try:
        validate_slug(slug)
    except ValueError as error:
        _fail("E_FORGE_CHANGE_INVALID_SLUG", str(error))
    forge_root = root / ".forge"
    changes_root = forge_root / "changes"
    if not forge_root.is_dir():
        _fail("E_FORGE_NOT_INITIALIZED", "Forge is not initialized. Run `forge init` first.")
    flow_id, flow_data = _active_flow(root)
    number = allocate_change_number(changes_root)
    change_id = f"CHG-{number:04d}"
    target = changes_root / f"{change_id}-{slug}"
    try:
        plan = render_scaffold(
            change_id=change_id,
            slug=slug,
            flow_id=flow_id,
            flow_data=flow_data,
            behavioral=not non_behavioral,
        )
    except ValueError as error:
        _fail("E_FORGE_CHANGE_INVALID_PATH", str(error))
    if target.exists():
        _fail("E_FORGE_CHANGE_CONFLICT", f"Change target already exists: {target}.")

    relative_target = target.relative_to(root).as_posix()
    if not changes_root.exists():
        typer.echo(f"CREATE forge_owned {changes_root.relative_to(root).as_posix()}/")
    for path in plan.files:
        typer.echo(f"CREATE forge_owned {relative_target}/{path}")
    try:
        publish_scaffold(target, plan)
    except FileExistsError:
        _fail("E_FORGE_CHANGE_CONFLICT", f"Change target appeared during publication: {target}.")
    except ChangeRollbackIncompleteError as error:
        _fail(error.code, f"Change publication rollback was incomplete: {error}.", INTERNAL_ERROR_EXIT_CODE)
    except OSError as error:
        _fail("E_FORGE_CHANGE_PUBLICATION", str(error), INTERNAL_ERROR_EXIT_CODE)
    except Exception as error:
        _fail("E_FORGE_INTERNAL_ERROR", str(error), INTERNAL_ERROR_EXIT_CODE)
    typer.echo(f"Created {change_id} at {relative_target}")
