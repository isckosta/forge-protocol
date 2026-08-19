from pathlib import Path
import re
import subprocess

import pytest
from typer.testing import CliRunner

import forge_cli.adapter_cli as adapter_cli
from forge_cli.adapters.publisher import (
    AdapterPublicationConflictError,
    AdapterPublicationStaleRecordError,
    UnsafeAdapterPathError,
)
from forge_cli.adapters.state import AdapterInstallationRecord, write_installation_record
from forge_cli.app import app
from forge_cli.git import GitUnavailableError


runner = CliRunner()


def _init_git_repository(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)


def _initialize_project(project: Path, monkeypatch) -> None:
    _init_git_repository(project)
    monkeypatch.chdir(project)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0, result.output


def _operation_lines(output: str) -> list[str]:
    return [line for line in output.splitlines() if line.split(" ", 1)[0] in {
        "CREATE", "UPDATE", "UNCHANGED", "PRESERVE", "CONFLICT", "DELETE_GENERATED",
    }]


def test_adapter_help_exposes_only_infrastructure_commands() -> None:
    result = runner.invoke(app, ["adapter", "--help"])

    assert result.exit_code == 0
    for name in ("list", "configure", "plan", "install", "validate", "doctor", "update"):
        assert name in result.stdout
    for forbidden in ("specify", "implement", "review"):
        assert forbidden not in result.stdout


def test_plan_and_install_dry_run_have_identical_operations(tmp_path: Path, monkeypatch) -> None:
    _initialize_project(tmp_path, monkeypatch)

    planned = runner.invoke(app, ["adapter", "plan", "codex"])
    dry_run = runner.invoke(app, ["adapter", "install", "codex", "--dry-run"])

    assert planned.exit_code == dry_run.exit_code == 0
    assert _operation_lines(planned.stdout) == _operation_lines(dry_run.stdout)
    assert not (tmp_path / ".agents").exists()


def test_adapter_configure_writes_a_safe_user_owned_target(tmp_path: Path, monkeypatch) -> None:
    _initialize_project(tmp_path, monkeypatch)

    result = runner.invoke(app, ["adapter", "configure", "codex", "--target", "tools/forge"])

    assert result.exit_code == 0
    assert "Configured codex target: tools/forge" in result.stdout
    assert (tmp_path / ".forge" / "adapters" / "codex" / "config.yml").is_file()


def test_adapter_list_reports_packaged_metadata_and_installation_state(tmp_path: Path, monkeypatch) -> None:
    _initialize_project(tmp_path, monkeypatch)

    result = runner.invoke(app, ["adapter", "list"])

    assert result.exit_code == 0
    assert "codex" in result.stdout
    assert "version" in result.stdout
    assert "harness" in result.stdout
    assert "protocol" in result.stdout
    assert "not_installed" in result.stdout


def test_adapter_list_treats_unsupported_project_protocol_as_unknown_compatibility(
    tmp_path: Path, monkeypatch
) -> None:
    _initialize_project(tmp_path, monkeypatch)
    config = tmp_path / ".forge" / "forge.yml"
    config.write_text(
        re.sub(r"protocol: \d+", "protocol: 99", config.read_text(encoding="utf-8")),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["adapter", "list"])

    assert result.exit_code == 0
    assert "compatibility=unknown" in result.stdout


@pytest.mark.parametrize(
    ("record_adapter_id", "record_harness"),
    (("other", "codex"), ("codex", "other")),
    ids=("adapter-id", "harness"),
)
def test_adapter_list_reports_mismatched_installation_identity_as_invalid(
    tmp_path: Path,
    monkeypatch,
    record_adapter_id: str,
    record_harness: str,
) -> None:
    _initialize_project(tmp_path, monkeypatch)
    record_path = tmp_path / ".forge" / "adapters" / "codex" / "installation.yml"
    write_installation_record(
        record_path,
        AdapterInstallationRecord(
            adapter_id=record_adapter_id,
            adapter_version="0.1.0",
            harness=record_harness,
            protocol_min=1,
            protocol_max_exclusive=2,
            publication_root=".agents/skills/forge",
            generated_artifacts=(),
            limitations=(),
        ),
    )
    before = record_path.read_bytes()

    result = runner.invoke(app, ["adapter", "list"])

    assert result.exit_code == 0
    assert "installation=invalid" in result.stdout
    assert record_path.read_bytes() == before


def test_adapter_install_is_idempotent_and_reports_unchanged_operations(
    tmp_path: Path, monkeypatch
) -> None:
    _initialize_project(tmp_path, monkeypatch)

    first = runner.invoke(app, ["adapter", "install", "codex"])
    listed = runner.invoke(app, ["adapter", "list"])
    skill = tmp_path / ".agents" / "skills" / "forge" / "SKILL.md"
    record = tmp_path / ".forge" / "adapters" / "codex" / "installation.yml"
    before = (skill.stat().st_mtime_ns, record.stat().st_mtime_ns)
    second = runner.invoke(app, ["adapter", "install", "codex"])

    assert first.exit_code == 0, first.output
    assert "installation=installed" in listed.stdout
    assert second.exit_code == 0, second.output
    assert _operation_lines(second.stdout)
    assert all(line.startswith("UNCHANGED forge_owned ") for line in _operation_lines(second.stdout))
    assert (skill.stat().st_mtime_ns, record.stat().st_mtime_ns) == before


def test_adapter_install_confirms_success_and_names_the_next_step(
    tmp_path: Path, monkeypatch
) -> None:
    _initialize_project(tmp_path, monkeypatch)

    result = runner.invoke(app, ["adapter", "install", "codex"])

    assert result.exit_code == 0, result.output
    assert "codex Adapter installed at .agents/skills/forge." in result.stdout
    assert "Open codex in this repository" in result.stdout
    lines = result.stdout.splitlines()
    confirmation_index = next(
        index for index, line in enumerate(lines) if "Adapter installed at" in line
    )
    assert _operation_lines("\n".join(lines[:confirmation_index]))
    assert "No changes required." not in result.stdout


def test_adapter_install_dry_run_prints_no_success_confirmation(
    tmp_path: Path, monkeypatch
) -> None:
    _initialize_project(tmp_path, monkeypatch)

    result = runner.invoke(app, ["adapter", "install", "codex", "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "Adapter installed at" not in result.stdout


def test_adapter_reinstall_prints_no_success_confirmation(
    tmp_path: Path, monkeypatch
) -> None:
    _initialize_project(tmp_path, monkeypatch)
    runner.invoke(app, ["adapter", "install", "codex"])

    result = runner.invoke(app, ["adapter", "install", "codex"])

    assert result.exit_code == 0, result.output
    assert "No changes required." in result.stdout
    assert "Adapter installed at" not in result.stdout


def test_adapter_conflict_is_reported_before_installation_and_does_not_mutate(
    tmp_path: Path, monkeypatch
) -> None:
    _initialize_project(tmp_path, monkeypatch)
    target = tmp_path / ".agents" / "skills" / "forge" / "SKILL.md"
    target.parent.mkdir(parents=True)
    target.write_text("user-owned", encoding="utf-8")

    result = runner.invoke(app, ["adapter", "install", "codex"])

    assert result.exit_code == 2
    assert "CONFLICT .agents/skills/forge/SKILL.md: ownership or expected-state conflict" in result.stdout
    assert "E_FORGE_ADAPTER_CONFLICT: Adapter plan contains unresolved conflicts." in result.stdout
    assert target.read_text(encoding="utf-8") == "user-owned"
    assert not (tmp_path / ".forge" / "adapters" / "codex" / "installation.yml").exists()


def test_adapter_unknown_and_project_errors_use_stable_codes(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)

    uninitialized = runner.invoke(app, ["adapter", "plan", "codex"])
    unknown_project = tmp_path / "initialized"
    unknown_project.mkdir()
    _initialize_project(unknown_project, monkeypatch)
    unknown = runner.invoke(app, ["adapter", "plan", "missing"])

    assert uninitialized.exit_code == 2
    assert "E_FORGE_NOT_INITIALIZED:" in uninitialized.stdout
    assert unknown.exit_code == 2
    assert "E_FORGE_ADAPTER_UNKNOWN:" in unknown.stdout


def test_adapter_validate_and_doctor_are_read_only_and_actionable(tmp_path: Path, monkeypatch) -> None:
    _initialize_project(tmp_path, monkeypatch)

    validated = runner.invoke(app, ["adapter", "validate", "codex"])
    diagnosed = runner.invoke(app, ["adapter", "doctor", "codex"])

    assert validated.exit_code == 2
    assert "E_FORGE_ADAPTER_NOT_INSTALLED:" in validated.stdout
    assert diagnosed.exit_code == 2
    assert "FAIL installation: Adapter is not installed. — Run `forge adapter install codex`." in diagnosed.stdout
    assert not (tmp_path / ".agents").exists()


def test_adapter_update_requires_an_existing_installation_record(tmp_path: Path, monkeypatch) -> None:
    _initialize_project(tmp_path, monkeypatch)

    result = runner.invoke(app, ["adapter", "update", "codex"])

    assert result.exit_code == 2
    assert "E_FORGE_ADAPTER_NOT_INSTALLED: Adapter update requires an existing installation record." in result.stdout
    assert not (tmp_path / ".agents").exists()


def test_adapter_git_environment_failure_uses_exit_code_three(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    def missing_git(_: Path) -> Path:
        raise GitUnavailableError("Git executable is unavailable.")

    monkeypatch.setattr(adapter_cli, "resolve_project_root", missing_git)
    result = runner.invoke(app, ["adapter", "plan", "codex"])

    assert result.exit_code == 3
    assert "E_FORGE_GIT_UNAVAILABLE: Git executable is unavailable." in result.stdout


def test_adapter_install_maps_publication_conflict_to_stable_conflict_exit_code(
    tmp_path: Path, monkeypatch
) -> None:
    _initialize_project(tmp_path, monkeypatch)

    def explode(*_args, **_kwargs):
        raise AdapterPublicationConflictError(
            "Adapter create target appeared after planning: tool/generated.md."
        )

    monkeypatch.setattr(adapter_cli.AdapterService, "install", explode)
    result = runner.invoke(app, ["adapter", "install", "codex"])

    assert result.exit_code == 2
    assert (
        "E_FORGE_ADAPTER_CONFLICT: Adapter create target appeared after planning: "
        "tool/generated.md." in result.stdout
    )


def test_adapter_install_maps_unsafe_path_to_stable_exit_code(
    tmp_path: Path, monkeypatch
) -> None:
    _initialize_project(tmp_path, monkeypatch)

    def explode(*_args, **_kwargs):
        raise UnsafeAdapterPathError("Adapter artifact path escapes repository root: '../escape'.")

    monkeypatch.setattr(adapter_cli.AdapterService, "install", explode)
    result = runner.invoke(app, ["adapter", "install", "codex"])

    assert result.exit_code == 2
    assert (
        "E_FORGE_ADAPTER_UNSAFE_PATH: Adapter artifact path escapes repository root: "
        "'../escape'." in result.stdout
    )


def test_adapter_update_maps_stale_record_to_stable_exit_code(
    tmp_path: Path, monkeypatch
) -> None:
    _initialize_project(tmp_path, monkeypatch)

    def explode(*_args, **_kwargs):
        raise AdapterPublicationStaleRecordError(
            "Existing installation record does not authorize update for tool/generated.md."
        )

    monkeypatch.setattr(adapter_cli.AdapterService, "update", explode)
    result = runner.invoke(app, ["adapter", "update", "codex"])

    assert result.exit_code == 2
    assert (
        "E_FORGE_ADAPTER_STALE_RECORD: Existing installation record does not authorize "
        "update for tool/generated.md." in result.stdout
    )


def test_adapter_command_maps_unexpected_project_preparation_failure_to_internal_error(
    tmp_path: Path, monkeypatch
) -> None:
    _initialize_project(tmp_path, monkeypatch)

    def explode(*_args, **_kwargs):
        raise RuntimeError("project preparation exploded")

    monkeypatch.setattr(adapter_cli, "validate_project", explode)
    result = runner.invoke(app, ["adapter", "plan", "codex"])

    assert result.exit_code == 70
    assert result.stdout == "E_FORGE_INTERNAL_ERROR: project preparation exploded\n"
    assert not isinstance(result.exception, RuntimeError)


def test_adapter_list_maps_unexpected_registry_preparation_failure_to_internal_error(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    def explode():
        raise RuntimeError("registry preparation exploded")

    monkeypatch.setattr(adapter_cli, "build_packaged_registry", explode)
    result = runner.invoke(app, ["adapter", "list"])

    assert result.exit_code == 70
    assert result.stdout == "E_FORGE_INTERNAL_ERROR: registry preparation exploded\n"
    assert not isinstance(result.exception, RuntimeError)


@pytest.mark.parametrize("adapter_id", ["codex", "claude-code"])
def test_adapter_install_then_doctor_succeeds_for_every_registered_adapter(
    adapter_id: str, tmp_path: Path, monkeypatch
) -> None:
    """CHG-0018 FR-008/C-074 (shared conformance): the real CLI install ->
    doctor round trip must work identically for every registered Adapter,
    not only Codex."""
    _initialize_project(tmp_path, monkeypatch)

    installed = runner.invoke(app, ["adapter", "install", adapter_id])
    assert installed.exit_code == 0, installed.output

    doctored = runner.invoke(app, ["adapter", "doctor", adapter_id])
    assert doctored.exit_code == 0, doctored.output
    assert "generated_drift" in doctored.stdout
    assert "FAIL" not in doctored.stdout

    reinstalled = runner.invoke(app, ["adapter", "install", adapter_id])
    assert reinstalled.exit_code == 0, reinstalled.output
    assert "No changes required." in reinstalled.stdout
