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


def test_tampering_between_freeze_and_completion_is_still_detected(tmp_path: Path) -> None:
    """CHG-0012-R001 (BLOCKER, found by independent Strict Review Iteration 1):
    the fix must not silently disable freeze protection for the Change's own
    reviewed files -- only for genuinely unrelated repository activity. This
    reproduces the Reviewer's own attack: the subject's own file, tampered
    with after Review passed but *before* the Change is sealed as complete,
    must still be caught.
    """
    root = tmp_path
    _init_repo(root)
    (root / "reviewed_module.py").write_text("original reviewed content\n", encoding="utf-8")
    frozen = _commit(root, "implementation")
    change_dir = "CHG-9011-example"
    manifest = _manifest("strict_review")  # not complete yet
    provenance = _provenance(frozen)
    _write_metadata_commit(root, change_dir, manifest, provenance, "record passed review")

    # Tamper with the Change's own reviewed file before it is sealed complete.
    (root / "reviewed_module.py").write_text("silently swapped content\n", encoding="utf-8")
    _commit(root, "tamper with the reviewed file before sealing complete")

    # Now seal it complete -- the tampering happened before this commit.
    manifest_complete = _manifest("complete")
    _write_metadata_commit(root, change_dir, manifest_complete, provenance, "seal complete after tampering")

    result = validate_project(root, resolve_protocol_root())

    assert any("review subject changed after its immutable revision freeze" in m for m in _messages(result)), _messages(result)


def test_tampering_after_completion_is_a_disclosed_residual_limitation(tmp_path: Path) -> None:
    """Documents the accepted, disclosed trade-off (not the R001 bypass):
    once a Change is genuinely sealed complete, further edits to its files
    are no longer this freeze check's concern -- that is a different
    Change's responsibility. This is intentionally different from
    CHG-0012-R001 (tampering *before* sealing, which must still be caught,
    per the test above)."""
    root = tmp_path
    _init_repo(root)
    (root / "reviewed_module.py").write_text("original reviewed content\n", encoding="utf-8")
    frozen = _commit(root, "implementation")
    change_dir = "CHG-9012-example"
    manifest_complete = _manifest("complete")
    provenance = _provenance(frozen)
    _write_metadata_commit(root, change_dir, manifest_complete, provenance, "seal complete immediately")

    # A later, independent Change edits the same file -- ordinary shared-file
    # evolution, not a bypass of this Change's own freeze.
    (root / "reviewed_module.py").write_text("legitimately evolved by a later Change\n", encoding="utf-8")
    _commit(root, "later Change edits the same shared file")

    result = validate_project(root, resolve_protocol_root())

    assert not any("review subject changed after its immutable revision freeze" in m for m in _messages(result)), _messages(result)


def test_reverting_and_resealing_complete_cannot_hide_tampering(tmp_path: Path) -> None:
    """CHG-0012-R002 (BLOCKER, found by independent Resolution Verification
    Iteration 2): state.current is hand-editable with no programmatic gate.
    Sealing complete, reverting to strict_review, tampering with the
    reviewed file, then re-sealing complete must not hide the tampering
    just because the *first* seal commit looked clean.
    """
    root = tmp_path
    _init_repo(root)
    (root / "reviewed_module.py").write_text("original reviewed content\n", encoding="utf-8")
    frozen = _commit(root, "implementation")
    change_dir = "CHG-9013-example"
    provenance = _provenance(frozen)

    _write_metadata_commit(root, change_dir, _manifest("complete"), provenance, "seal complete (clean)")
    _write_metadata_commit(root, change_dir, _manifest("strict_review"), provenance, "revert to strict_review")

    (root / "reviewed_module.py").write_text("silently swapped after revert\n", encoding="utf-8")
    _commit(root, "tamper with the reviewed file while reverted")

    _write_metadata_commit(root, change_dir, _manifest("complete"), provenance, "re-seal complete (hiding the tamper)")

    result = validate_project(root, resolve_protocol_root())

    assert any("review subject changed after its immutable revision freeze" in m for m in _messages(result)), _messages(result)


def test_active_change_still_detects_freeze_drift(tmp_path: Path) -> None:
    """Regression guard: this exemption must not weaken the freeze for a
    Change that has not completed -- CHG-0008/CHG-0011's active-review
    protections must remain exactly as strict as before."""
    root = tmp_path
    _setup(root, state_current="strict_review")

    result = validate_project(root, resolve_protocol_root())

    assert any("review subject changed after its immutable revision freeze" in m for m in _messages(result)), _messages(result)
