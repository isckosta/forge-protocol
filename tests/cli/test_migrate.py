from pathlib import Path
import subprocess

from typer.testing import CliRunner

from forge_cli.app import app


runner = CliRunner()


def _init_git_repository(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)


def _write_v1_provenance(change_dir: Path) -> None:
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


def test_migrate_check_reports_no_migration_available(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["migrate", "--check"])

    assert result.exit_code == 0
    assert result.stdout == "No migration available.\n"


def test_migrate_check_reports_a_real_candidate_without_applying_it(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    change_dir = tmp_path / ".forge" / "changes" / "CHG-0001-example"
    _write_v1_provenance(change_dir)

    result = runner.invoke(app, ["migrate", "--check"])

    assert result.exit_code == 0
    assert "AVAILABLE CHG-0001-example" in result.stdout
    assert "forge/execution-provenance@2" in result.stdout
    assert (change_dir / "provenance.yml").read_text(encoding="utf-8").startswith(
        "schema: forge/execution-provenance@1"
    )


def test_migrate_applies_the_real_candidate(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    change_dir = tmp_path / ".forge" / "changes" / "CHG-0001-example"
    _write_v1_provenance(change_dir)

    result = runner.invoke(app, ["migrate"])

    assert result.exit_code == 0
    assert "MIGRATED CHG-0001-example" in result.stdout
    assert (change_dir / "provenance.yml").read_text(encoding="utf-8").startswith(
        "schema: forge/execution-provenance@2"
    )


def test_migrate_is_idempotent(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    change_dir = tmp_path / ".forge" / "changes" / "CHG-0001-example"
    _write_v1_provenance(change_dir)

    runner.invoke(app, ["migrate"])
    second = runner.invoke(app, ["migrate"])

    assert second.exit_code == 0
    assert second.stdout == "Nothing to migrate.\n"


def test_migrate_never_touches_a_delegated_task_record(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    change_dir = tmp_path / ".forge" / "changes" / "CHG-0002-example"
    change_dir.mkdir(parents=True)
    original = (
        "schema: forge/execution-provenance@1\n"
        "change: CHG-0002\n"
        "records:\n"
        "  - id: r1\n"
        "    role: implementation\n"
        "    execution: {id: e1, context_id: c1}\n"
        "  - id: r2\n"
        "    role: delegated_task\n"
        "    execution: {id: e2, context_id: c2}\n"
    )
    (change_dir / "provenance.yml").write_text(original, encoding="utf-8")

    result = runner.invoke(app, ["migrate"])

    assert result.exit_code == 0
    assert result.stdout == "Nothing to migrate.\n"
    assert (change_dir / "provenance.yml").read_text(encoding="utf-8") == original


def test_migrate_requires_a_git_repository(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["migrate", "--check"])

    assert result.exit_code == 3
    assert "E_FORGE_NOT_GIT_REPOSITORY" in result.stdout
