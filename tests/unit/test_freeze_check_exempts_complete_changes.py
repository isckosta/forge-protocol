"""CHG-0012: a passed Review Iteration's frozen-subject-drift check must not
fire once the Change's own state.current is complete -- unrelated activity
elsewhere in the repository (other Changes continuing development on the
same branch) is expected and must not resurrect a closed Change as a
validation failure.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from forge_cli.protocol_resources import resolve_protocol_root
from forge_cli.validation import validate_project


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "commit", "--allow-empty", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def _init_repo(root: Path) -> None:
    _git(root, "init", "-q")
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
    _commit(root, "init")


def _manifest(state_current: str) -> dict:
    return {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": "CHG-9010", "title": "T", "kind": "bugfix"},
        "flow": {"initial": "fast", "current": "fast", "escalations": []},
        "state": {"current": state_current},
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
            "iterations": [
                {
                    "id": "review-001",
                    "revision": "chg-9010-impl-001",
                    "subject_provenance": "impl-001",
                    "reviewer_provenance": "review-001",
                    "status": "passed",
                }
            ],
        },
        "documentation": {"impact_evaluated": True, "update_required": False},
    }


def _provenance(commit: str) -> dict:
    def _record(record_id: str, role: str, execution: str, context: str) -> dict:
        return {
            "id": record_id,
            "role": role,
            "execution": {"id": execution, "context_id": context},
            "recorded_at": "2026-08-18T00:00:00Z",
            "revision": {
                "id": "chg-9010-impl-001",
                "immutable_ref": {"type": "git_commit", "value": commit},
                "commit": commit,
            },
            "source": {"assurance": "recorded", "observed_by": "self"},
        }

    return {
        "schema": "forge/execution-provenance@1",
        "change": "CHG-9010",
        "records": [
            _record("impl-001", "implementation", "impl-exec", "impl-ctx"),
            _record("review-001", "review", "review-exec", "review-ctx"),
        ],
    }


def _write_metadata_commit(root: Path, change_dir: str, manifest: dict, provenance: dict, message: str) -> str:
    change = root / ".forge/changes" / change_dir
    change.mkdir(parents=True, exist_ok=True)
    (change / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (change / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    return _commit(root, message)


def _setup(root: Path, state_current: str) -> None:
    _init_repo(root)
    frozen = _commit(root, "implementation")
    change_dir = "CHG-9010-example"
    manifest = _manifest(state_current)
    provenance = _provenance(frozen)
    _write_metadata_commit(root, change_dir, manifest, provenance, "record passed review")
    # Unrelated activity elsewhere in the repository, outside this Change's
    # three review-control-metadata paths -- exactly what happens when other
    # Changes continue development on the same branch after this one merges.
    (root / "unrelated.py").write_text("print('unrelated work')\n", encoding="utf-8")
    _commit(root, "unrelated later work by a different Change")


def _messages(result) -> list[str]:
    return [f.message for f in result.findings]


def test_complete_change_is_exempt_from_post_completion_freeze_drift(tmp_path: Path) -> None:
    root = tmp_path
    _setup(root, state_current="complete")

    result = validate_project(root, resolve_protocol_root())

    assert not any("review subject changed after its immutable revision freeze" in m for m in _messages(result)), _messages(result)


def test_active_change_still_detects_freeze_drift(tmp_path: Path) -> None:
    """Regression guard: this exemption must not weaken the freeze for a
    Change that has not completed -- CHG-0008/CHG-0011's active-review
    protections must remain exactly as strict as before."""
    root = tmp_path
    _setup(root, state_current="strict_review")

    result = validate_project(root, resolve_protocol_root())

    assert any("review subject changed after its immutable revision freeze" in m for m in _messages(result)), _messages(result)
