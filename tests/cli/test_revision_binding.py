import subprocess
from pathlib import Path

import yaml
from typer.testing import CliRunner

from forge_cli.app import app


runner = CliRunner()


def _init_project(project_root: Path) -> None:
    subprocess.run(["git", "init", str(project_root)], check=True, capture_output=True, text=True)
    forge_dir = project_root / ".forge"
    forge_dir.mkdir(parents=True)
    (forge_dir / "forge.yml").write_text(
        "schema: forge/project@1\n"
        "project:\n"
        "  name: revision-binding-red\n"
        "forge:\n"
        "  protocol: 2\n"
        "flows:\n"
        "  default: full\n"
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


def _write_change(project_root: Path, subject_commit: str, reviewer_commit: str) -> None:
    change_dir = project_root / ".forge" / "changes" / "CHG-9999-revision-binding"
    change_dir.mkdir(parents=True)
    manifest = {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": "CHG-9999", "title": "Revision binding", "kind": "bugfix"},
        "flow": {"initial": "full", "current": "full", "escalations": []},
        "state": {"current": "strict_review"},
        "artifacts": {},
        "tdd": {"status": "compliant", "cycles": 1},
        "verification": {"status": "passed"},
        "review": {
            "status": "passed",
            "iteration": 1,
            "blockers": 0,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "iterations": [{
                "id": "review-001",
                "revision": "revision-a",
                "subject_provenance": "resolution-001",
                "reviewer_provenance": "review-001",
                "status": "passed",
            }],
        },
        "documentation": {"impact_evaluated": True, "update_required": False},
    }
    provenance = {
        "schema": "forge/execution-provenance@1",
        "change": "CHG-9999",
        "records": [
            {
                "id": "resolution-001",
                "role": "resolution",
                "execution": {"id": "resolution-exec", "context_id": "resolution-context"},
                "recorded_at": "2026-08-15T19:00:00Z",
                "revision": {"id": "revision-a", "commit": subject_commit},
                "source": {"assurance": "recorded", "observed_by": "self"},
            },
            {
                "id": "review-001",
                "role": "review",
                "execution": {"id": "review-exec", "context_id": "review-context"},
                "recorded_at": "2026-08-15T19:01:00Z",
                "revision": {"id": "revision-a", "commit": reviewer_commit},
                "source": {"assurance": "recorded", "observed_by": "self"},
            },
        ],
    }
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")


def test_protocol2_rejects_same_logical_revision_with_different_commits(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)
    _write_change(tmp_path, "a" * 40, "b" * 40)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "commit" in result.stdout.lower() or "immutable" in result.stdout.lower()
