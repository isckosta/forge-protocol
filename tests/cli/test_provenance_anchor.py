import subprocess
from pathlib import Path

import yaml
from typer.testing import CliRunner

from forge_cli.app import app

runner = CliRunner()


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _init(root: Path) -> None:
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


def _commit(root: Path, message: str) -> str:
    _git(root, "add", ".")
    _git(root, "commit", "--allow-empty", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def _record(record_id: str, role: str, revision: str, commit: str) -> dict:
    return {
        "id": record_id,
        "role": role,
        "execution": {"id": f"{record_id}-exec", "context_id": f"{record_id}-ctx"},
        "recorded_at": "2026-08-15T20:15:00Z",
        "revision": {
            "id": revision,
            "immutable_ref": {"type": "git_commit", "value": commit},
            "commit": commit,
        },
        "source": {"assurance": "recorded", "observed_by": "self"},
    }


def _write_change(root: Path, commit: str, *, passed: bool) -> Path:
    change = root / ".forge/changes/CHG-9999-anchor"
    change.mkdir(parents=True, exist_ok=True)
    iteration = {
        "id": "review-001",
        "revision": "revision-a",
        "subject_provenance": "resolution-001",
        "status": "passed" if passed else "pending",
    }
    records = [_record("resolution-001", "resolution", "revision-a", commit)]
    if passed:
        iteration["reviewer_provenance"] = "review-001"
        records.append(_record("review-001", "review", "revision-a", commit))
    manifest = {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": "CHG-9999", "title": "Anchor", "kind": "bugfix"},
        "flow": {"initial": "full", "current": "full", "escalations": []},
        "state": {"current": "strict_review"},
        "artifacts": {},
        "tdd": {"status": "compliant", "cycles": 1},
        "verification": {"status": "passed"},
        "review": {
            "status": "passed" if passed else "pending",
            "iteration": 1,
            "blockers": 0,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "iterations": [iteration],
        },
        "documentation": {"impact_evaluated": True, "update_required": False},
    }
    (change / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (change / "provenance.yml").write_text(
        yaml.safe_dump({"schema": "forge/execution-provenance@1", "change": "CHG-9999", "records": records}, sort_keys=False),
        encoding="utf-8",
    )
    return change


def _validate(root: Path, monkeypatch):
    monkeypatch.chdir(root)
    return runner.invoke(app, ["validate"])


def _anchored_change(tmp_path: Path) -> tuple[Path, str]:
    _init(tmp_path)
    (tmp_path / "subject.txt").write_text("frozen\n", encoding="utf-8")
    frozen = _commit(tmp_path, "freeze subject A")
    change = _write_change(tmp_path, frozen, passed=False)
    _commit(tmp_path, "record subject provenance for A")
    return change, frozen


def test_rewriting_frozen_subject_provenance_cannot_move_baseline(tmp_path, monkeypatch):
    _, _ = _anchored_change(tmp_path)
    subject = tmp_path / "subject.txt"
    subject.write_text("reviewable mutation B\n", encoding="utf-8")
    moved = _commit(tmp_path, "reviewable mutation B")
    _write_change(tmp_path, moved, passed=True)
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 2
    assert "immutable subject provenance" in result.stdout.lower()


def test_mutating_anchored_subject_fields_fails(tmp_path, monkeypatch):
    change, _ = _anchored_change(tmp_path)
    path = change / "provenance.yml"
    provenance = yaml.safe_load(path.read_text())
    provenance["records"][0]["execution"]["id"] = "replacement-exec"
    path.write_text(yaml.safe_dump(provenance, sort_keys=False))
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 2
    assert "immutable subject provenance" in result.stdout.lower()


def test_replacing_anchored_resolution_role_fails(tmp_path, monkeypatch):
    change, _ = _anchored_change(tmp_path)
    path = change / "provenance.yml"
    provenance = yaml.safe_load(path.read_text())
    provenance["records"][0]["role"] = "review"
    path.write_text(yaml.safe_dump(provenance, sort_keys=False))
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 2
    assert "immutable subject provenance" in result.stdout.lower()


def test_historical_iteration_cannot_switch_subject_record(tmp_path, monkeypatch):
    change, frozen = _anchored_change(tmp_path)
    ppath = change / "provenance.yml"
    provenance = yaml.safe_load(ppath.read_text())
    provenance["records"].append(_record("resolution-002", "resolution", "revision-a", frozen))
    ppath.write_text(yaml.safe_dump(provenance, sort_keys=False))
    mpath = change / "manifest.yml"
    manifest = yaml.safe_load(mpath.read_text())
    manifest["review"]["iterations"][0]["subject_provenance"] = "resolution-002"
    mpath.write_text(yaml.safe_dump(manifest, sort_keys=False))
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 2
    assert "immutable review iteration subject binding" in result.stdout.lower()


def test_legitimate_review_record_append_preserves_subject_anchor(tmp_path, monkeypatch):
    _, frozen = _anchored_change(tmp_path)
    _write_change(tmp_path, frozen, passed=True)
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 0, result.stdout


def test_removing_anchored_subject_record_fails(tmp_path, monkeypatch):
    change, _ = _anchored_change(tmp_path)
    ppath = change / "provenance.yml"
    provenance = yaml.safe_load(ppath.read_text())
    provenance["records"] = []
    ppath.write_text(yaml.safe_dump(provenance, sort_keys=False))
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 2
    assert "subject provenance was not found" in result.stdout.lower()


def test_shallow_history_fails_closed_for_anchored_subject(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    _anchored_change(source)
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "--depth", "1", f"file://{source}", str(clone)],
        check=True,
        capture_output=True,
        text=True,
    )
    result = _validate(clone, monkeypatch)
    assert result.exit_code == 2
    assert "authority" in result.stdout.lower()


def test_malformed_history_after_first_anchor_does_not_erase_authority(tmp_path, monkeypatch):
    change, frozen = _anchored_change(tmp_path)
    # A later malformed historical manifest must not invalidate an authority that
    # was already established in an earlier committed representation.
    (change / "manifest.yml").write_text("review: [broken\n", encoding="utf-8")
    _commit(tmp_path, "malformed later review metadata")
    _write_change(tmp_path, frozen, passed=True)
    result = _validate(tmp_path, monkeypatch)
    assert result.exit_code == 0, result.stdout
