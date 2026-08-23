"""Contributor-facing FER commands."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Annotated

import typer
import yaml

from forge_cli.experience.configuration import (
    ExperienceConfigurationError,
    load_experience_configuration,
    write_experience_configuration,
)
from forge_cli.experience.context import collect_context
from forge_cli.experience.markdown import render_markdown
from forge_cli.experience.model import ExperienceInputError, parse_record_input
from forge_cli.experience.storage import ExperienceStorage, ExperienceStorageError
from forge_cli.git import NotGitRepositoryError, resolve_project_root


experience_app = typer.Typer(help="Opt-in contributor evidence about real Forge experience.")


def _root() -> Path:
    try:
        return resolve_project_root(Path.cwd())
    except NotGitRepositoryError:
        typer.echo("E_FORGE_NOT_GIT_REPOSITORY: current directory is not inside a Git repository.")
        raise typer.Exit(code=3)


@experience_app.command()
def enable() -> None:
    """Enable local Forge Experience Reporting for this repository."""
    path = write_experience_configuration(_root(), True)
    typer.echo(f"Forge experience reporting enabled: {path}")


@experience_app.command()
def disable() -> None:
    """Disable local Forge Experience Reporting for this repository."""
    path = write_experience_configuration(_root(), False)
    typer.echo(f"Forge experience reporting disabled: {path}")


@experience_app.command()
def status() -> None:
    """Show whether local Forge Experience Reporting is enabled."""
    try:
        configuration = load_experience_configuration(_root())
    except ExperienceConfigurationError as error:
        typer.echo(f"E_FORGE_EXPERIENCE_CONFIGURATION: {error}")
        raise typer.Exit(code=2)
    typer.echo("Forge experience reporting: enabled" if configuration.enabled else "Forge experience reporting: disabled")


@experience_app.command()
def record(
    input_path: Annotated[Path, typer.Option("--input", help="YAML input path, or '-' for stdin.")],
    change: str | None = typer.Option(None, "--change"),
    flow: str | None = typer.Option(None, "--flow"),
    adapter: str | None = typer.Option(None, "--adapter"),
    harness: str | None = typer.Option(None, "--harness"),
    execution: str | None = typer.Option(None, "--execution"),
    context_id: str | None = typer.Option(None, "--context"),
    report: str | None = typer.Option(None, "--report", help="Existing FER report ID for another entry."),
) -> None:
    """Record one contributor-authored material observation or positive evidence."""
    root = _root()
    try:
        configuration = load_experience_configuration(root)
    except ExperienceConfigurationError as error:
        typer.echo(f"E_FORGE_EXPERIENCE_CONFIGURATION: {error}")
        raise typer.Exit(code=2)
    if not configuration.enabled:
        typer.echo("E_FORGE_EXPERIENCE_DISABLED: enable FER before recording evidence.")
        raise typer.Exit(code=2)
    try:
        raw = sys.stdin.read() if str(input_path) == "-" else input_path.read_text(encoding="utf-8")
        entry = parse_record_input(yaml.safe_load(raw))
        context = collect_context(
            root,
            change=change,
            flow=flow,
            adapter=adapter,
            harness=harness,
            execution=execution,
            context_id=context_id,
        )
        path = ExperienceStorage(root, context=context, report_id=report).record(entry)
    except (OSError, yaml.YAMLError, ExperienceInputError, ExperienceStorageError) as error:
        typer.echo(f"E_FORGE_EXPERIENCE_RECORD: {error}")
        raise typer.Exit(code=2)
    typer.echo(f"Forge experience report recorded: {path.relative_to(root)}")


@experience_app.command()
def render(
    report: str | None = typer.Argument(None, help="FER report ID, such as FER-0001."),
    all_reports: bool = typer.Option(False, "--all", help="Render every canonical FER report."),
) -> None:
    """Regenerate human-readable Markdown from canonical FER YAML."""
    if report is not None and all_reports:
        typer.echo("E_FORGE_EXPERIENCE_RENDER: choose one report or --all, not both.")
        raise typer.Exit(code=2)
    root = _root()
    reports_root = root / "dogfooding" / "reports"
    if not reports_root.exists():
        typer.echo("No Forge experience reports found.")
        return
    if reports_root.is_symlink() or not reports_root.is_dir():
        typer.echo(f"E_FORGE_EXPERIENCE_RENDER: invalid FER report directory: {reports_root}")
        raise typer.Exit(code=2)
    if report is None and not all_reports:
        typer.echo("E_FORGE_EXPERIENCE_RENDER: provide a report ID or --all.")
        raise typer.Exit(code=2)
    if report is not None:
        try:
            ExperienceStorage(root, context={}, report_id=report)
        except ExperienceStorageError as error:
            typer.echo(f"E_FORGE_EXPERIENCE_RENDER: invalid report ID: {error}")
            raise typer.Exit(code=2)

    paths = (
        sorted(reports_root.glob("FER-*.yml"))
        if all_reports
        else [reports_root / f"{report}.yml"]
    )
    errors: list[str] = []
    rendered = 0
    for path in paths:
        if path.is_symlink() or not path.is_file():
            errors.append(f"{path}: canonical FER report is missing or symlinked")
            continue
        try:
            storage = ExperienceStorage(root, context={}, report_id=path.stem)
            with storage._file_lock(path):
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
                if (
                    not isinstance(document, dict)
                    or document.get("report") != path.stem
                    or not ExperienceStorage._valid_document(document)
                ):
                    raise ExperienceStorageError(f"{path}: invalid FER schema")
                storage._atomic_write_markdown(path.with_suffix(".md"), render_markdown(document))
            rendered += 1
        except (OSError, yaml.YAMLError, ExperienceStorageError) as error:
            errors.append(str(error))
    if errors:
        for error in errors:
            typer.echo(error)
        raise typer.Exit(code=2)
    typer.echo(f"Rendered {rendered} Forge experience report Markdown file(s)")


@experience_app.command(name="validate")
def validate_reports() -> None:
    """Validate explicitly requested FER reports without affecting project validation."""
    root = _root()
    reports_root = root / "dogfooding" / "reports"
    if not reports_root.exists():
        typer.echo("No Forge experience reports found.")
        return
    errors: list[str] = []
    if (root / "dogfooding").is_symlink() or reports_root.is_symlink():
        typer.echo(f"{reports_root}: invalid FER report directory symlink")
        raise typer.Exit(code=2)
    for path in sorted(reports_root.glob("FER-*.yml")):
        if path.is_symlink():
            errors.append(f"{path}: symlinked FER reports are not allowed")
            continue
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
            if (
                not isinstance(document, dict)
                or document.get("schema") != "forge/experience-report@1"
                or document.get("report") != path.stem
                or not isinstance(document.get("source"), dict)
                or not isinstance(document.get("observations"), list)
                or not isinstance(document.get("positive_evidence"), list)
                or not isinstance(document.get("follow_up_candidates"), list)
                or not ExperienceStorage._valid_document(document)
            ):
                errors.append(f"{path}: invalid FER schema")
        except (OSError, yaml.YAMLError) as error:
            errors.append(f"{path}: {error}")
    if errors:
        for error in errors:
            typer.echo(error)
        raise typer.Exit(code=2)
    typer.echo("Forge experience reports are valid")
