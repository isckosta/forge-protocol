from pathlib import Path
import subprocess

from typer.testing import CliRunner

import forge_cli.adapter_cli as adapter_cli
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
    config.write_text(config.read_text(encoding="utf-8").replace("protocol: 1", "protocol: 99"), encoding="utf-8")

    result = runner.invoke(app, ["adapter", "list"])

    assert result.exit_code == 0
    assert "compatibility=unknown" in result.stdout


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
