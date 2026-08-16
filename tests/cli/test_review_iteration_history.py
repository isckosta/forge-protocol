import subprocess
from pathlib import Path

import yaml
from typer.testing import CliRunner

from forge_cli.app import app

runner = CliRunner()


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _commit(root: Path, message: str) -> str:
    _git(root, "add", ".")
    _git(root, "commit", "--allow-empty", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def _record(commit: str) -> dict:
    return {
        "id": "resolution-001",
        "role": "resolution",
        "execution": {"id": "resolution-exec", "context_id": "resolution-context"},
        "recorded_at": "2026-08-15T20:15:00Z",
        "revision": {
            "id": "revision-a",
            "immutable_ref": {"type": "git_commit", "value": commit},
            "commit": commit,
        },
        "source": {"assurance": "recorded", "observed_by": "self"},
    }


def _write_manifest(root: Path, iteration_id: str) -> Path:
    change = root / ".forge/changes/CHG-9998-review-id"
    change.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": "CHG-9998", "title": "Review ID", "kind": "bugfix"},
        "flow": {"initial": "full", "current": "full", "escalations": []},
        "state": {"current": "strict_review"},
        "artifacts": {},
        "tdd": {"status": "compliant", "cycles": 1},
        "verification": {"status": "passed"},
        "review": {
            "status": "failed",
            "iteration": 1,
            "blockers": 0,
            "majors": 1,
            "minors": 0,
            "observations": 0,
            "iterations": [
                {
                    "id": iteration_id,
                    "revision": "revision-a",
                    "subject_provenance": "resolution-001",
                    "status": "failed",
                    "evidence_gap": "blocking finding",
                }
            ],
        },
        "documentation": {"impact_evaluated": True, "update_required": False},
    }
    path = change / "manifest.yml"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return change


def _init_failed_review(root: Path) -> Path:
    _git(root, "init")
    _git(root, "config", "user.email", "t@x")
    _git(root, "config", "user.name", "T")
    forge = root / ".forge"
    forge.mkdir()
    (forge / "forge.yml").write_text(
        "schema: forge/project@1\nproject:\n  name: t\nforge:\n  protocol: 2\n"
        "flows:\n  default: full\n  allow_fast: true\n  auto_escalation: true\n"
        "testing:\n  approach: tdd_first\nreview:\n  strict: true\n"
        "documentation:\n  impact_evaluation: required\n",
        encoding="utf-8",
    )
    (root / "subject.txt").write_text("subject A\n", encoding="utf-8")
    frozen = _commit(root, "freeze subject")
    change = _write_manifest(root, "review-001")
    (change / "provenance.yml").write_text(
        yaml.safe_dump(
            {
                "schema": "forge/execution-provenance@1",
                "change": "CHG-9998",
                "records": [_record(frozen)],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    _commit(root, "record failed review binding")
    return change


def test_historical_failed_iteration_id_cannot_be_replaced(tmp_path, monkeypatch):
    _init_failed_review(tmp_path)
    _write_manifest(tmp_path, "review-002")

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2
    assert "review iteration" in result.stdout.lower()
    assert "authority" in result.stdout.lower() or "identity" in result.stdout.lower()
