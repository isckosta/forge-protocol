import subprocess
from pathlib import Path

import yaml
from typer.testing import CliRunner

import forge_cli.app as app_module

runner = CliRunner()


def _init_git_repository(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)


def _write_manifest(root: Path, directory: str, review: dict) -> Path:
    change_dir = root / ".forge" / "changes" / directory
    change_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": directory.split("-")[0] + "-" + directory.split("-")[1], "title": "Fixture", "kind": "feature"},
        "flow": {"initial": "standard", "current": "standard", "escalations": []},
        "state": {"current": "intent"},
        "artifacts": {},
        "requirements": {"total": 0, "implemented": 0, "verified": 0},
        "tdd": {"status": "pending"},
        "verification": {"status": "pending"},
        "review": review,
        "documentation": {"impact_evaluated": False},
    }
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return change_dir


def _base_project(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app_module.app, ["init"]).exit_code == 0


def test_review_status_reports_populated_change(tmp_path: Path, monkeypatch) -> None:
    """CHG-0050 TDD-013 (FR-006, AC-016)."""
    _base_project(tmp_path, monkeypatch)
    _write_manifest(
        tmp_path,
        "CHG-9001-populated",
        {
            "status": "active",
            "iteration": 1,
            "blockers": 1,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "mode": "thorough",
            "current_phase": "findings_recorded",
            "iterations": [{"id": "review-001", "revision": "rev-1", "status": "failed"}],
        },
    )

    result = runner.invoke(app_module.app, ["change", "review-status", "CHG-9001-populated"])

    assert result.exit_code == 0, result.output
    assert "thorough" in result.stdout
    assert "strict" in result.stdout
    assert "Findings" in result.stdout
    assert "BLOCKER: 1" in result.stdout
    assert "Resolution" in result.stdout


def test_review_status_reports_not_yet_started(tmp_path: Path, monkeypatch) -> None:
    """CHG-0050 TDD-013 (FR-006, AC-016b)."""
    _base_project(tmp_path, monkeypatch)
    _write_manifest(
        tmp_path,
        "CHG-9002-fresh",
        {
            "status": "pending",
            "iteration": 0,
            "blockers": 0,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "mode": "recommended",
            "iterations": [],
        },
    )

    result = runner.invoke(app_module.app, ["change", "review-status", "CHG-9002-fresh"])

    assert result.exit_code == 0, result.output
    assert "Review not yet started" in result.stdout


def test_review_status_fails_cleanly_for_a_nonexistent_change(tmp_path: Path, monkeypatch) -> None:
    """CHG-0050 TDD-013 (FR-006, AC-017)."""
    _base_project(tmp_path, monkeypatch)

    result = runner.invoke(app_module.app, ["change", "review-status", "CHG-0000-does-not-exist"])

    assert result.exit_code != 0
    assert (tmp_path / ".forge" / "changes" / "CHG-0000-does-not-exist").exists() is False


def test_review_status_reports_stopped_as_incomplete(tmp_path: Path, monkeypatch) -> None:
    """CHG-0050 TDD-014 (FR-007, AC-019)."""
    _base_project(tmp_path, monkeypatch)
    _write_manifest(
        tmp_path,
        "CHG-9003-stopped",
        {
            "status": "failed",
            "iteration": 1,
            "blockers": 1,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "mode": "fast",
            "current_phase": "stopped",
            "iterations": [{"id": "review-001", "revision": "rev-1", "status": "failed"}],
        },
    )

    result = runner.invoke(app_module.app, ["change", "review-status", "CHG-9003-stopped"])

    assert result.exit_code == 0, result.output
    assert "not complete" in result.stdout.lower()
    assert "BLOCKER: 1" in result.stdout


def test_forge_validate_accepts_stopped_phase_with_non_passed_status(tmp_path: Path, monkeypatch) -> None:
    """CHG-0050 TDD-014 (FR-007, AC-018)."""
    _base_project(tmp_path, monkeypatch)
    _write_manifest(
        tmp_path,
        "CHG-9004-stopped-validate",
        {
            "status": "failed",
            "iteration": 1,
            "blockers": 1,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "current_phase": "stopped",
            "iterations": [{"id": "review-001", "revision": "rev-1", "status": "failed"}],
        },
    )

    result = runner.invoke(app_module.app, ["validate"])

    assert result.exit_code == 0, result.output
