"""Public Typer commands for packaged Harness Adapters."""

from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import Annotated

import typer

from forge_cli.adapters.configuration import (
    AdapterConfiguration,
    InvalidAdapterConfigurationError,
    write_adapter_configuration,
)
from forge_cli.adapters.formatting import doctor_lines, plan_lines, validation_lines
from forge_cli.adapters.manifest import is_protocol_compatible
from forge_cli.adapters.packaged import build_packaged_registry
from forge_cli.adapters.registry import AdapterRegistry, UnknownAdapterError
from forge_cli.adapters.repository import (
    AdapterRepositoryError,
    load_optional_installation_record,
)
from forge_cli.adapters.service import (
    AdapterService,
    InvalidAdapterInstallationError,
    require_valid_installation_identity,
)
from forge_cli.configuration import (
    InvalidProjectConfigurationError,
    UnsupportedProtocolVersionError,
    load_project_configuration,
)
from forge_cli.git import GitUnavailableError, NotGitRepositoryError, resolve_project_root
from forge_cli.protocol_resources import resolve_protocol_root
from forge_cli.protocol_resolution import ProtocolResolutionError
from forge_cli.validation import validate_project


DOMAIN_ERROR_EXIT_CODE = 2
ENVIRONMENT_ERROR_EXIT_CODE = 3
INTERNAL_ERROR_EXIT_CODE = 70

adapter_app = typer.Typer(help="Manage packaged Harness Adapter representations.")


def _echo_error(code: str, message: str, *, exit_code: int = DOMAIN_ERROR_EXIT_CODE) -> None:
    typer.echo(f"{code}: {message}")
    raise typer.Exit(code=exit_code)


def _project_root() -> Path:
    try:
        return resolve_project_root(Path.cwd())
    except GitUnavailableError:
        _echo_error(
            "E_FORGE_GIT_UNAVAILABLE",
            "Git executable is unavailable.",
            exit_code=ENVIRONMENT_ERROR_EXIT_CODE,
        )
    except NotGitRepositoryError:
        _echo_error(
            "E_FORGE_NOT_GIT_REPOSITORY",
            "current directory is not inside a Git repository.",
            exit_code=ENVIRONMENT_ERROR_EXIT_CODE,
        )
    raise AssertionError("unreachable")


def _initialized_project_root() -> Path:
    root = _project_root()
    validation = validate_project(root, resolve_protocol_root())
    if not validation.passed:
        finding = validation.findings[0]
        _echo_error(finding.code, finding.message)
    return root


def _service() -> tuple[AdapterRegistry, AdapterService]:
    registry = build_packaged_registry()
    return registry, AdapterService(registry)


def _handle_adapter_error(error: Exception) -> None:
    if isinstance(error, AdapterRepositoryError):
        _echo_error("E_FORGE_ADAPTER_INSTALLATION_INVALID", str(error))
    if isinstance(error, ProtocolResolutionError):
        _echo_error("E_FORGE_ADAPTER_CONFORMANCE", str(error))
    code = getattr(error, "code", None)
    if isinstance(code, str):
        _echo_error(code, str(error))
    _echo_error("E_FORGE_INTERNAL_ERROR", str(error), exit_code=INTERNAL_ERROR_EXIT_CODE)


def _command_boundary(command):
    """Map every Adapter command's preparation and execution failures."""
    @wraps(command)
    def wrapped(*args, **kwargs):
        try:
            return command(*args, **kwargs)
        except typer.Exit:
            raise
        except Exception as error:
            _handle_adapter_error(error)

    return wrapped


def _emit_plan_and_fail_conflicts(plan) -> None:
    for line in plan_lines(plan):
        typer.echo(line)
    if plan.conflicts:
        _echo_error("E_FORGE_ADAPTER_CONFLICT", "Adapter plan contains unresolved conflicts.")


@adapter_app.command("list")
@_command_boundary
def list_adapters() -> None:
    """List packaged Adapters and observed repository installation state."""
    registry, _ = _service()
    project_configuration: dict | None = None
    project_root: Path | None = None
    try:
        project_root = resolve_project_root(Path.cwd())
        project_configuration = load_project_configuration(
            project_root / ".forge" / "forge.yml"
        )
    except (
        GitUnavailableError,
        NotGitRepositoryError,
        InvalidProjectConfigurationError,
        UnsupportedProtocolVersionError,
    ):
        pass

    for driver in registry.list():
        manifest = driver.manifest
        compatibility = "unknown"
        installation = "not_installed"
        if project_configuration is not None:
            compatibility = (
                "compatible"
                if is_protocol_compatible(manifest, project_configuration["forge"]["protocol"])
                else "incompatible"
            )
        if project_root is not None:
            try:
                record = load_optional_installation_record(project_root, manifest.adapter_id)
                if record is not None:
                    require_valid_installation_identity(record, driver)
            except (AdapterRepositoryError, InvalidAdapterInstallationError):
                installation = "invalid"
            else:
                if record is not None:
                    installation = (
                        "installed" if record.adapter_version == manifest.version else "stale"
                    )
        typer.echo(
            f"{manifest.adapter_id} version={manifest.version} harness={manifest.harness} "
            f"protocol=[{manifest.protocol_min}, {manifest.protocol_max_exclusive}) "
            f"compatibility={compatibility} installation={installation}"
        )


@adapter_app.command()
@_command_boundary
def configure(
    adapter_id: Annotated[str, typer.Argument(metavar="ADAPTER")],
    target: Annotated[str | None, typer.Option("--target")] = None,
) -> None:
    """Write a user-owned Adapter configuration."""
    root = _initialized_project_root()
    registry, _ = _service()
    try:
        registry.get(adapter_id)
        write_adapter_configuration(
            root,
            AdapterConfiguration(adapter_id=adapter_id, target=target),
        )
    except (UnknownAdapterError, InvalidAdapterConfigurationError) as error:
        _handle_adapter_error(error)
    typer.echo(f"Configured {adapter_id} target: {target if target is not None else 'packaged default'}")


@adapter_app.command()
@_command_boundary
def plan(
    adapter_id: Annotated[str, typer.Argument(metavar="ADAPTER")],
    target: Annotated[str | None, typer.Option("--target")] = None,
) -> None:
    """Print the read-only Adapter publication plan."""
    root = _initialized_project_root()
    _, service = _service()
    try:
        result = service.plan(root, adapter_id, explicit_target=target)
    except Exception as error:
        _handle_adapter_error(error)
    _emit_plan_and_fail_conflicts(result.plan)


@adapter_app.command()
@_command_boundary
def install(
    adapter_id: Annotated[str, typer.Argument(metavar="ADAPTER")],
    target: Annotated[str | None, typer.Option("--target")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Install an Adapter projection after showing its plan."""
    root = _initialized_project_root()
    registry, service = _service()
    try:
        planned = service.plan(root, adapter_id, explicit_target=target)
        _emit_plan_and_fail_conflicts(planned.plan)
        result = service.install(root, adapter_id, explicit_target=target, dry_run=dry_run)
    except typer.Exit:
        raise
    except Exception as error:
        _handle_adapter_error(error)
    if not result.mutated:
        typer.echo("No changes required.")
        return
    harness = registry.get(adapter_id).manifest.harness
    typer.echo(f"{adapter_id} Adapter installed at {result.target}.")
    typer.echo(
        f"Open {harness} in this repository to begin a Forge-governed Change; "
        "no further Forge-side step is required."
    )


@adapter_app.command()
@_command_boundary
def validate(adapter_id: Annotated[str, typer.Argument(metavar="ADAPTER")]) -> None:
    """Validate Adapter installation state without modifying it."""
    root = _initialized_project_root()
    _, service = _service()
    try:
        result = service.validate(root, adapter_id)
    except Exception as error:
        _handle_adapter_error(error)
    if result.passed:
        typer.echo("Adapter installation is valid")
        return
    for line in validation_lines(result):
        typer.echo(line)
    raise typer.Exit(code=DOMAIN_ERROR_EXIT_CODE)


@adapter_app.command()
@_command_boundary
def doctor(adapter_id: Annotated[str, typer.Argument(metavar="ADAPTER")]) -> None:
    """Diagnose Adapter installation state without modifying it."""
    root = _initialized_project_root()
    _, service = _service()
    try:
        result = service.doctor(root, adapter_id)
    except Exception as error:
        _handle_adapter_error(error)
    for line in doctor_lines(result):
        typer.echo(line)
    if not result.passed:
        raise typer.Exit(code=DOMAIN_ERROR_EXIT_CODE)


@adapter_app.command()
@_command_boundary
def update(
    adapter_id: Annotated[str, typer.Argument(metavar="ADAPTER")],
    target: Annotated[str | None, typer.Option("--target")] = None,
) -> None:
    """Update an installed Adapter projection after showing its plan."""
    root = _initialized_project_root()
    _, service = _service()
    try:
        planned = service.plan(root, adapter_id, explicit_target=target)
        _emit_plan_and_fail_conflicts(planned.plan)
        result = service.update(root, adapter_id, explicit_target=target)
    except typer.Exit:
        raise
    except Exception as error:
        _handle_adapter_error(error)
    if not result.mutated:
        typer.echo("No changes required.")
