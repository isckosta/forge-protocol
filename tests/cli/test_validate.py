import subprocess
from pathlib import Path

from typer.testing import CliRunner

from forge_cli.app import app


runner = CliRunner()


def _init_git_repository(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)


def _write_valid_project_configuration(project_root: Path) -> None:
    forge_dir = project_root / ".forge"
    forge_dir.mkdir(parents=True)
    (forge_dir / "forge.yml").write_text(
        "schema: forge/project@1\n"
        "project:\n"
        "  name: example\n"
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
        "  impact_evaluation: required\n",
        encoding="utf-8",
    )


def test_validate_reports_success_for_valid_forge_project(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_valid_project_configuration(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 0
    assert "Forge project is valid" in result.stdout


def test_validate_reports_not_initialized_with_exit_code_two(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2
    assert "E_FORGE_NOT_INITIALIZED" in result.stdout
    assert ".forge/" in result.stdout
