import subprocess
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from forge_cli.app import app


runner = CliRunner()


def _init_project(project_root: Path, protocol: int = 2) -> None:
    subprocess.run(["git", "init", str(project_root)], check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "forge@example.test"], cwd=project_root, check=True)
    subprocess.run(["git", "config", "user.name", "Forge Test"], cwd=project_root, check=True)
    forge_dir = project_root / ".forge"
    forge_dir.mkdir(parents=True)
    (forge_dir / "forge.yml").write_text(
        "schema: forge/project@1\nproject:\n  name: revision-binding\nforge:\n"
        f"  protocol: {protocol}\n"
        "flows:\n  default: full\n  allow_fast: true\n  auto_escalation: true\n"
        "testing:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n",
        encoding="utf-8",
    )


def _commit_all(project_root: Path, message: str) -> str:
    subprocess.run(["git", "add", "."], cwd=project_root, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=project_root, check=True, capture_output=True, text=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=project_root, check=True, capture_output=True, text=True).stdout.strip()


def _manifest(flow: str = "full", status: str = "passed", revision: str = "revision-a") -> dict:
    return {
        "schema": "forge/change@2", "protocol": 2,
        "change": {"id": "CHG-9999", "title": "Revision binding", "kind": "bugfix"},
        "flow": {"initial": flow, "current": flow, "escalations": []},
        "state": {"current": "strict_review"}, "artifacts": {},
        "tdd": {"status": "compliant", "cycles": 1}, "verification": {"status": "passed"},
        "review": {"status": status, "iteration": 1, "blockers": 0, "majors": 0, "minors": 0, "observations": 0,
            "iterations": [{"id": "review-001", "revision": revision, "subject_provenance": "resolution-001", "reviewer_provenance": "review-001" if status == "passed" else None, "status": status}]},
        "documentation": {"impact_evaluated": True, "update_required": False},
    }


def _record(record_id: str, role: str, revision: str, commit: str, execution: str, context: str) -> dict:
    return {"id": record_id, "role": role, "execution": {"id": execution, "context_id": context},
        "recorded_at": "2026-08-15T19:00:00Z",
        "revision": {"id": revision, "immutable_ref": {"type": "git_commit", "value": commit}, "commit": commit},
        "source": {"assurance": "recorded", "observed_by": "self"}}


def _write_bound_change(project_root: Path, subject_commit: str, reviewer_commit: str | None = None, *, flow: str = "full", status: str = "passed", subject_revision: str = "revision-a", reviewer_revision: str = "revision-a", shared_execution: bool = False, shared_context: bool = False) -> Path:
    change_dir = project_root / ".forge" / "changes" / "CHG-9999-revision-binding"
    change_dir.mkdir(parents=True, exist_ok=True)
    manifest = _manifest(flow=flow, status=status)
    if status != "passed":
        manifest["review"]["iterations"][0].pop("reviewer_provenance")
    records = [_record("resolution-001", "resolution", subject_revision, subject_commit, "shared" if shared_execution else "resolution-exec", "shared-context" if shared_context else "resolution-context")]
    if reviewer_commit is not None:
        records.append(_record("review-001", "review", reviewer_revision, reviewer_commit, "shared" if shared_execution else "review-exec", "shared-context" if shared_context else "review-context"))
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (change_dir / "provenance.yml").write_text(yaml.safe_dump({"schema": "forge/execution-provenance@1", "change": "CHG-9999", "records": records}, sort_keys=False), encoding="utf-8")
    return change_dir


def _validate(project_root: Path, monkeypatch):
    monkeypatch.chdir(project_root)
    return runner.invoke(app, ["validate"])


def test_protocol2_rejects_same_logical_revision_with_different_commits(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)
    seed = _commit_all(tmp_path, "seed")
    other = _commit_all(tmp_path, "other")
    _write_bound_change(tmp_path, seed, other)
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 2
    assert "C-026" in result.stdout and "immutable" in result.stdout.lower()


def test_protocol2_accepts_same_logical_revision_and_same_commit(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)
    subject = _commit_all(tmp_path, "subject")
    _write_bound_change(tmp_path, subject, subject)
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 0


def test_protocol2_rejects_missing_immutable_ref(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)
    subject = _commit_all(tmp_path, "subject")
    change_dir = _write_bound_change(tmp_path, subject, subject)
    provenance = yaml.safe_load((change_dir / "provenance.yml").read_text())
    provenance["records"][0]["revision"].pop("immutable_ref")
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False))
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 2 and "C-026" in result.stdout


def test_protocol2_rejects_reviewer_wrong_commit(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)
    subject = _commit_all(tmp_path, "subject")
    wrong = _commit_all(tmp_path, "wrong")
    _write_bound_change(tmp_path, subject, wrong)
    assert _validate(tmp_path, monkeypatch).exit_code == 2


def test_protocol2_rejects_subject_wrong_commit(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)
    subject = _commit_all(tmp_path, "subject")
    wrong = "f" * 40
    _write_bound_change(tmp_path, wrong, wrong)
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 2 and "does not exist" in result.stdout.lower()


def test_protocol2_pending_review_bound_to_current_subject_passes(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)
    subject = _commit_all(tmp_path, "subject")
    _write_bound_change(tmp_path, subject, status="pending")
    assert _validate(tmp_path, monkeypatch).exit_code == 0


def test_protocol2_commit_after_subject_freeze_requires_new_provenance(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)
    subject = _commit_all(tmp_path, "subject")
    change_dir = _write_bound_change(tmp_path, subject, status="pending")
    (tmp_path / "src.txt").write_text("changed after freeze", encoding="utf-8")
    _commit_all(tmp_path, "mutate subject")
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 2 and "changed after" in result.stdout.lower()


def test_protocol2_review_metadata_after_freeze_does_not_mutate_subject(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)
    subject = _commit_all(tmp_path, "subject")
    change_dir = _write_bound_change(tmp_path, subject, status="pending")
    (change_dir / "review.md").write_text("review metadata", encoding="utf-8")
    _commit_all(tmp_path, "review metadata")
    assert _validate(tmp_path, monkeypatch).exit_code == 0


def test_protocol2_rereview_targets_resolution2_concrete_commit(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path)
    first = _commit_all(tmp_path, "resolution one")
    second = _commit_all(tmp_path, "resolution two")
    _write_bound_change(tmp_path, second, second)
    assert _validate(tmp_path, monkeypatch).exit_code == 0


@pytest.mark.parametrize("flow", ["fast", "standard", "full"])
def test_protocol2_revision_binding_applies_to_every_flow(tmp_path: Path, monkeypatch, flow: str) -> None:
    _init_project(tmp_path)
    subject = _commit_all(tmp_path, "subject")
    _write_bound_change(tmp_path, subject, subject, flow=flow)
    assert _validate(tmp_path, monkeypatch).exit_code == 0


def test_protocol1_remains_compatible_without_provenance(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path, protocol=1)
    assert _validate(tmp_path, monkeypatch).exit_code == 0


def test_protocol2_shared_execution_still_fails(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path); subject = _commit_all(tmp_path, "subject")
    _write_bound_change(tmp_path, subject, subject, shared_execution=True)
    assert _validate(tmp_path, monkeypatch).exit_code == 2


def test_protocol2_shared_context_still_fails(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path); subject = _commit_all(tmp_path, "subject")
    _write_bound_change(tmp_path, subject, subject, shared_context=True)
    assert _validate(tmp_path, monkeypatch).exit_code == 2


def test_protocol2_wrong_revision_id_still_fails(tmp_path: Path, monkeypatch) -> None:
    _init_project(tmp_path); subject = _commit_all(tmp_path, "subject")
    _write_bound_change(tmp_path, subject, subject, reviewer_revision="revision-b")
    assert _validate(tmp_path, monkeypatch).exit_code == 2
