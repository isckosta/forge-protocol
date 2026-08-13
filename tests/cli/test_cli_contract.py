from pathlib import Path
import subprocess

from typer.testing import CliRunner

import forge_cli.app as app_module


runner = CliRunner()


def _init_git_repository(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)


def test_cli_exposes_only_infrastructure_commands() -> None:
    result = runner.invoke(app_module.app, ["--help"])

    assert result.exit_code == 0
    for command in ("version", "init", "validate", "doctor"):
        assert command in result.stdout

    for forbidden in ("change", "specify", "test-design", "implement", "verify", "review", "resolve", "complete"):
        assert forbidden not in result.stdout


def test_init_creates_a_valid_forge_project_from_nested_directory(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    nested = tmp_path / "services" / "api"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    init_result = runner.invoke(app_module.app, ["init"])

    assert init_result.exit_code == 0
    assert (tmp_path / ".forge" / "forge.yml").is_file()
    assert (tmp_path / ".forge" / "flows" / "fast.yml").is_file()
    assert (tmp_path / ".forge" / "flows" / "standard.yml").is_file()
    assert (tmp_path / ".forge" / "flows" / "full.yml").is_file()

    validate_result = runner.invoke(app_module.app, ["validate"])
    assert validate_result.exit_code == 0
    assert "Forge project is valid" in validate_result.stdout


def test_environment_failure_uses_exit_code_three(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app_module.app, ["validate"])

    assert result.exit_code == 3
    assert "E_FORGE_NOT_GIT_REPOSITORY" in result.stdout


def test_unexpected_internal_failure_uses_distinct_exit_code(monkeypatch, tmp_path: Path) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)

    def explode(*args, **kwargs):
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(app_module, "validate_project", explode)

    result = runner.invoke(app_module.app, ["validate"])

    assert result.exit_code == 70
    assert "E_FORGE_INTERNAL_ERROR" in result.stdout
