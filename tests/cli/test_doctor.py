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


def test_doctor_reports_non_git_environment_without_modifying_files(tmp_path: Path, monkeypatch) -> None:
    marker = tmp_path / "marker.txt"
    marker.write_text("unchanged", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 2
    assert "FAIL git_repository" in result.stdout
    assert marker.read_text(encoding="utf-8") == "unchanged"
