from pathlib import Path
import subprocess

from typer.testing import CliRunner

from forge_cli.app import app


runner = CliRunner()


def _init_git_repository(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)


def test_doctor_reports_failed_and_skipped_checks_with_exit_code_two(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 2
    assert "PASS git_available" in result.stdout
    assert "PASS git_repository" in result.stdout
    assert "FAIL forge_initialized" in result.stdout
    assert "SKIP project_configuration" in result.stdout


def test_doctor_exit_code_reflects_drifted_adapter_installation(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["adapter", "install", "codex"])
    skill = tmp_path / ".agents" / "skills" / "forge" / "SKILL.md"
    skill.write_bytes(skill.read_bytes() + b"\n# deliberate drift\n")

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 2
    assert "FAIL adapter:codex:generated_drift" in result.stdout


def test_doctor_reports_migration_advisory_without_failing(tmp_path: Path, monkeypatch) -> None:
    """CHG-0019 FR-004: non-blocking WARN when a migration candidate exists."""
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    change_dir = tmp_path / ".forge" / "changes" / "CHG-0001-example"
    change_dir.mkdir(parents=True)
    (change_dir / "provenance.yml").write_text(
        "schema: forge/execution-provenance@1\n"
        "change: CHG-0001\n"
        "records:\n"
        "  - id: implementation-001\n"
        "    role: implementation\n"
        "    execution: {id: e1, context_id: c1}\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "WARN migration_available: 1 migration candidate(s) found" in result.stdout


def test_doctor_reports_no_migration_advisory_when_nothing_pending(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "migration_available" not in result.stdout


def test_doctor_reports_non_git_environment_without_modifying_files(tmp_path: Path, monkeypatch) -> None:
    marker = tmp_path / "marker.txt"
    marker.write_text("unchanged", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 2
    assert "FAIL git_repository" in result.stdout
    assert marker.read_text(encoding="utf-8") == "unchanged"


import os as _os

import pytest as _pytest

_posix_only = _pytest.mark.skipif(
    _os.name != "posix", reason="executable-bit checks are POSIX-only"
)


@_posix_only
def test_doctor_flags_non_executable_claude_code_hook(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["adapter", "install", "claude-code"])
    hook = tmp_path / ".claude/skills/forge/hooks/check-manifest-edit.sh"
    hook.chmod(0o644)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 2
    assert "FAIL adapter:claude-code:executable_artifacts" in result.stdout


@_posix_only
def test_doctor_passes_executable_check_for_fresh_claude_code_install(
    tmp_path: Path, monkeypatch
) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["adapter", "install", "claude-code"])

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "PASS adapter:claude-code:executable_artifacts" in result.stdout
