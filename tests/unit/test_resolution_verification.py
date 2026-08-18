"""CHG-0011: Resolution Verification scope, out-of-scope escalation, and
review convergence termination semantics.

Mirrors the real-Git-repository style already used by
tests/cli/test_review_iteration_history.py: every scenario is built from
real commits so the mechanism under test (git diff/log against local
history) is exercised for real, not mocked.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from forge_cli.protocol_resources import resolve_protocol_root
from forge_cli.validation import validate_project

BASE_FORGE_YML = """schema: forge/project@1
project:
  name: t
forge:
  protocol: 2
flows:
  default: full
  allow_fast: true
  auto_escalation: true
testing:
  approach: tdd_first
review:
  strict: true
documentation:
  impact_evaluation: required
"""

FORGE_YML_ALLOW_RESIDUAL_RISK = BASE_FORGE_YML.replace(
    "review:\n  strict: true\n",
    "review:\n  strict: true\n  convergence:\n    allow_residual_risk_acceptance: true\n",
)


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "commit", "--allow-empty", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def _init_repo(root: Path, forge_yml: str = BASE_FORGE_YML) -> None:
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@x")
    _git(root, "config", "user.name", "T")
    forge = root / ".forge"
    forge.mkdir()
    (forge / "forge.yml").write_text(forge_yml, encoding="utf-8")
    _commit(root, "init")


def _freeze_commit(root: Path, files: dict[str, str], message: str) -> str:
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return _commit(root, message)


def _record(
    record_id: str,
    role: str,
    commit: str,
    revision_id: str,
    execution: str,
    context: str,
    extra: dict | None = None,
) -> dict:
    rec = {
        "id": record_id,
        "role": role,
        "execution": {"id": execution, "context_id": context},
        "recorded_at": "2026-08-17T00:00:00Z",
        "revision": {
            "id": revision_id,
            "immutable_ref": {"type": "git_commit", "value": commit},
            "commit": commit,
        },
        "source": {"assurance": "recorded", "observed_by": "self"},
    }
    if extra:
        rec.update(extra)
    return rec


def _provenance(change_id: str, records: list[dict]) -> dict:
    return {"schema": "forge/execution-provenance@1", "change": change_id, "records": records}


def _manifest(change_id: str, iterations: list[dict], top_status: str = "active", convergence: dict | None = None) -> dict:
    m = {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": change_id, "title": "T", "kind": "bugfix"},
        "flow": {"initial": "full", "current": "full", "escalations": []},
        "state": {"current": "strict_review"},
        "artifacts": {},
        "tdd": {"status": "compliant", "cycles": 1},
        "verification": {"status": "passed"},
        "review": {
            "status": top_status,
            "iteration": len(iterations),
            "blockers": 0,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "iterations": iterations,
        },
        "documentation": {"impact_evaluated": True, "update_required": False},
    }
    if convergence is not None:
        m["review"]["convergence"] = convergence
    return m


def _write_metadata_commit(root: Path, change_dir: str, manifest: dict, provenance: dict, message: str) -> str:
    change = root / ".forge/changes" / change_dir
    change.mkdir(parents=True, exist_ok=True)
    (change / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (change / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    return _commit(root, message)


def _first_iteration(commit: str, revision_id: str = "chg-9001-impl-001") -> dict:
    return {
        "id": "review-001",
        "revision": revision_id,
        "subject_provenance": "impl-001",
        "status": "failed",
        "evidence_gap": "CHG-9001-R001 blocker",
    }


def _impl_record(commit: str, revision_id: str = "chg-9001-impl-001") -> dict:
    return _record("impl-001", "implementation", commit, revision_id, "impl-exec", "impl-ctx")


def _messages(result) -> list[str]:
    return [f.message for f in result.findings]


# ---------------------------------------------------------------------------
# TDD-012 — legacy manifests (this repository's own CHG-0008 / CHG-0010) are
# unaffected: no finding introduced by this Change's new logic.
# ---------------------------------------------------------------------------

def test_legacy_manifests_are_unaffected() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = validate_project(repo_root, resolve_protocol_root())
    new_logic_markers = (
        "resolution_verification", "Resolution Delta", "Out-of-Scope",
        "convergence", "Convergence Limit",
    )
    offending = [m for m in _messages(result) if any(marker in m for marker in new_logic_markers)]
    assert offending == [], offending


# ---------------------------------------------------------------------------
# TDD-013 — golden path: declared scope covers the real delta, independent
# Execution/Context, PASS.
# ---------------------------------------------------------------------------

def test_scoped_resolution_verification_passes(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    a1 = _freeze_commit(root, {"src/feature.py": "v1\n"}, "implementation")
    change_dir = "CHG-9001-golden"
    manifest_v1 = _manifest("CHG-9001", [_first_iteration(a1)])
    provenance_v1 = _provenance("CHG-9001", [_impl_record(a1)])
    _write_metadata_commit(root, change_dir, manifest_v1, provenance_v1, "freeze review 1")

    a2 = _freeze_commit(root, {"src/feature.py": "v2 fixed\n"}, "resolution")
    manifest_v2 = _manifest(
        "CHG-9001",
        [
            _first_iteration(a1),
            {
                "id": "review-002",
                "revision": "chg-9001-resolution-001",
                "subject_provenance": "resolution-001",
                "reviewer_provenance": "review-002",
                "kind": "resolution_verification",
                "status": "passed",
            },
        ],
        top_status="passed",
    )
    provenance_v2 = _provenance(
        "CHG-9001",
        [
            _impl_record(a1),
            _record(
                "resolution-001", "resolution", a2, "chg-9001-resolution-001",
                "resolution-exec", "resolution-ctx",
                extra={"scope": ["src/feature.py"], "targets": ["CHG-9001-R001"]},
            ),
            _record("review-002", "review", a2, "chg-9001-resolution-001", "review-exec-2", "review-ctx-2"),
        ],
    )
    _write_metadata_commit(root, change_dir, manifest_v2, provenance_v2, "record resolution + verification")

    result = validate_project(root, resolve_protocol_root())
    assert result.passed, _messages(result)


# ---------------------------------------------------------------------------
# TDD-016 — out-of-scope material mutation: passed-without-escalation fails;
# failed+full_review_required passes; a further resolution_verification is
# rejected; a following initial_review is accepted.
# ---------------------------------------------------------------------------

def _out_of_scope_setup(tmp_path: Path):
    root = tmp_path
    _init_repo(root)
    a1 = _freeze_commit(root, {"src/feature.py": "v1\n"}, "implementation")
    change_dir = "CHG-9002-oos"
    manifest_v1 = _manifest("CHG-9002", [_first_iteration(a1, "chg-9002-impl-001")])
    manifest_v1["change"]["id"] = "CHG-9002"
    provenance_v1 = _provenance("CHG-9002", [_impl_record(a1, "chg-9002-impl-001")])
    _write_metadata_commit(root, change_dir, manifest_v1, provenance_v1, "freeze review 1")

    # Resolution touches an undeclared file in addition to the declared one.
    a2 = _freeze_commit(root, {"src/feature.py": "v2 fixed\n", "src/unrelated.py": "surprise\n"}, "resolution")
    resolution_record = _record(
        "resolution-001", "resolution", a2, "chg-9002-resolution-001",
        "resolution-exec", "resolution-ctx",
        extra={"scope": ["src/feature.py"], "targets": ["CHG-9002-R001"]},
    )
    return root, change_dir, manifest_v1, a1, a2, resolution_record


def test_out_of_scope_mutation_cannot_be_silently_passed(tmp_path: Path) -> None:
    root, change_dir, manifest_v1, a1, a2, resolution_record = _out_of_scope_setup(tmp_path)
    manifest_v2 = _manifest(
        "CHG-9002",
        [
            manifest_v1["review"]["iterations"][0],
            {
                "id": "review-002", "revision": "chg-9002-resolution-001",
                "subject_provenance": "resolution-001", "reviewer_provenance": "review-002",
                "kind": "resolution_verification", "status": "passed",
            },
        ],
        top_status="passed",
    )
    provenance_v2 = _provenance("CHG-9002", [
        _impl_record(a1, "chg-9002-impl-001"), resolution_record,
        _record("review-002", "review", a2, "chg-9002-resolution-001", "review-exec-2", "review-ctx-2"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v2, provenance_v2, "illegitimate silent pass")

    result = validate_project(root, resolve_protocol_root())
    assert not result.passed
    assert any("Out-of-Scope Mutation" in m for m in _messages(result))


def test_out_of_scope_mutation_with_full_review_required_validates(tmp_path: Path) -> None:
    root, change_dir, manifest_v1, a1, a2, resolution_record = _out_of_scope_setup(tmp_path)
    manifest_v2 = _manifest(
        "CHG-9002",
        [
            manifest_v1["review"]["iterations"][0],
            {
                "id": "review-002", "revision": "chg-9002-resolution-001",
                "subject_provenance": "resolution-001", "reviewer_provenance": "review-002",
                "kind": "resolution_verification", "status": "failed",
                "full_review_required": True, "new_material_findings": 1,
                "evidence_gap": "CHG-9002-R002 (class C): src/unrelated.py touched outside declared scope",
            },
        ],
    )
    provenance_v2 = _provenance("CHG-9002", [
        _impl_record(a1, "chg-9002-impl-001"), resolution_record,
        _record("review-002", "review", a2, "chg-9002-resolution-001", "review-exec-2", "review-ctx-2"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v2, provenance_v2, "honest escalation")

    result = validate_project(root, resolve_protocol_root())
    assert result.passed, _messages(result)

    # A further resolution_verification against the same escalated subject is rejected...
    a3 = _freeze_commit(root, {"src/feature.py": "v3\n"}, "second resolution attempt")
    bad_next = _manifest(
        "CHG-9002",
        manifest_v2["review"]["iterations"] + [{
            "id": "review-003", "revision": "chg-9002-resolution-002",
            "subject_provenance": "resolution-002", "reviewer_provenance": "review-003",
            "kind": "resolution_verification", "status": "passed",
        }],
        top_status="passed",
    )
    bad_provenance = _provenance("CHG-9002", provenance_v2["records"] + [
        _record("resolution-002", "resolution", a3, "chg-9002-resolution-002", "resolution-exec-2", "resolution-ctx-2",
                extra={"scope": ["src/feature.py"], "targets": ["CHG-9002-R002"]}),
        _record("review-003", "review", a3, "chg-9002-resolution-002", "review-exec-3", "review-ctx-3"),
    ])
    _write_metadata_commit(root, change_dir, bad_next, bad_provenance, "illegal second resolution_verification")
    result2 = validate_project(root, resolve_protocol_root())
    assert not result2.passed
    assert any("further resolution_verification" in m for m in _messages(result2))


# ---------------------------------------------------------------------------
# TDD-020 (subset) — provenance/shape adversarial matrix.
# ---------------------------------------------------------------------------

def test_resolution_verification_rejected_as_first_iteration(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    a1 = _freeze_commit(root, {"src/x.py": "v1\n"}, "implementation")
    change_dir = "CHG-9003-first"
    manifest = _manifest("CHG-9003", [{
        "id": "review-001", "revision": "chg-9003-impl-001",
        "subject_provenance": "impl-001", "reviewer_provenance": "review-001",
        "kind": "resolution_verification", "status": "passed",
    }], top_status="passed")
    provenance = _provenance("CHG-9003", [
        _record("impl-001", "implementation", a1, "chg-9003-impl-001", "impl-exec", "impl-ctx"),
        _record("review-001", "review", a1, "chg-9003-impl-001", "review-exec", "review-ctx"),
    ])
    _write_metadata_commit(root, change_dir, manifest, provenance, "misclassified first iteration")

    result = validate_project(root, resolve_protocol_root())
    assert not result.passed
    assert any("MUST NOT be the first Review Iteration" in m for m in _messages(result))


def test_resolution_verification_rejects_implementation_subject(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    a1 = _freeze_commit(root, {"src/x.py": "v1\n"}, "implementation")
    change_dir = "CHG-9004-implsubject"
    manifest_v1 = _manifest("CHG-9004", [{
        "id": "review-001", "revision": "chg-9004-impl-001",
        "subject_provenance": "impl-001", "status": "failed",
    }])
    provenance_v1 = _provenance("CHG-9004", [_record("impl-001", "implementation", a1, "chg-9004-impl-001", "impl-exec", "impl-ctx")])
    _write_metadata_commit(root, change_dir, manifest_v1, provenance_v1, "freeze")

    a2 = _freeze_commit(root, {"src/x.py": "v2\n"}, "second implementation, not a resolution")
    manifest_v2 = _manifest("CHG-9004", manifest_v1["review"]["iterations"] + [{
        "id": "review-002", "revision": "chg-9004-impl-002",
        "subject_provenance": "impl-002", "reviewer_provenance": "review-002",
        "kind": "resolution_verification", "status": "passed",
    }], top_status="passed")
    provenance_v2 = _provenance("CHG-9004", provenance_v1["records"] + [
        _record("impl-002", "implementation", a2, "chg-9004-impl-002", "impl-exec-2", "impl-ctx-2"),
        _record("review-002", "review", a2, "chg-9004-impl-002", "review-exec-2", "review-ctx-2"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v2, provenance_v2, "misclassified implementation subject")

    result = validate_project(root, resolve_protocol_root())
    assert not result.passed
    assert any("implementation-role subject is definitionally an initial_review" in m for m in _messages(result))


def test_resolution_verification_requires_scope_and_targets(tmp_path: Path) -> None:
    root, change_dir, manifest_v1, a1, a2, resolution_record = _out_of_scope_setup(tmp_path)
    resolution_record.pop("scope")
    manifest_v2 = _manifest("CHG-9002", manifest_v1["review"]["iterations"] + [{
        "id": "review-002", "revision": "chg-9002-resolution-001",
        "subject_provenance": "resolution-001", "reviewer_provenance": "review-002",
        "kind": "resolution_verification", "status": "passed",
    }], top_status="passed")
    provenance_v2 = _provenance("CHG-9002", [
        _impl_record(a1, "chg-9002-impl-001"), resolution_record,
        _record("review-002", "review", a2, "chg-9002-resolution-001", "review-exec-2", "review-ctx-2"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v2, provenance_v2, "missing scope")

    result = validate_project(root, resolve_protocol_root())
    assert not result.passed
    assert any("declare non-empty scope and targets" in m for m in _messages(result))


def test_declared_convergence_counter_disagreement_is_rejected(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    a1 = _freeze_commit(root, {"src/x.py": "v1\n"}, "implementation")
    change_dir = "CHG-9005-counter"
    manifest_v1 = _manifest("CHG-9005", [{
        "id": "review-001", "revision": "chg-9005-impl-001",
        "subject_provenance": "impl-001", "status": "failed",
    }])
    provenance_v1 = _provenance("CHG-9005", [_record("impl-001", "implementation", a1, "chg-9005-impl-001", "impl-exec", "impl-ctx")])
    _write_metadata_commit(root, change_dir, manifest_v1, provenance_v1, "freeze")

    a2 = _freeze_commit(root, {"src/x.py": "v2\n"}, "resolution 1")
    manifest_v2 = _manifest(
        "CHG-9005",
        manifest_v1["review"]["iterations"] + [{
            "id": "review-002", "revision": "chg-9005-resolution-001",
            "subject_provenance": "resolution-001", "reviewer_provenance": "review-002",
            "kind": "resolution_verification", "status": "failed",
            "new_material_findings": 1,
            "evidence_gap": "CHG-9005-R002 (class B): regression inside delta",
        }],
        convergence={"state": "nominal", "consecutive_unconverged_verifications": 0},
    )
    provenance_v2 = _provenance("CHG-9005", provenance_v1["records"] + [
        _record("resolution-001", "resolution", a2, "chg-9005-resolution-001", "resolution-exec", "resolution-ctx",
                extra={"scope": ["src/x.py"], "targets": ["CHG-9005-R001"]}),
        _record("review-002", "review", a2, "chg-9005-resolution-001", "review-exec-2", "review-ctx-2"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v2, provenance_v2, "understated counter")

    result = validate_project(root, resolve_protocol_root())
    assert not result.passed
    assert any("is derived, not self-declared" in m for m in _messages(result))


# ---------------------------------------------------------------------------
# Convergence limit end-to-end: two consecutive unconverged Verifications ->
# review_convergence_failed; blocked passed status; blocked further
# resolution_verification; decision required; accept_residual_risk gated by
# project policy.
# ---------------------------------------------------------------------------

def _build_two_strike_manifest(root: Path, change_dir: str):
    a1 = _freeze_commit(root, {"src/x.py": "v1\n"}, "implementation")
    manifest_v1 = _manifest("CHG-9006", [{
        "id": "review-001", "revision": "chg-9006-impl-001",
        "subject_provenance": "impl-001", "status": "failed",
    }])
    provenance_v1 = _provenance("CHG-9006", [_record("impl-001", "implementation", a1, "chg-9006-impl-001", "impl-exec", "impl-ctx")])
    _write_metadata_commit(root, change_dir, manifest_v1, provenance_v1, "freeze")

    a2 = _freeze_commit(root, {"src/x.py": "v2\n"}, "resolution 1")
    it2 = {
        "id": "review-002", "revision": "chg-9006-resolution-001",
        "subject_provenance": "resolution-001", "reviewer_provenance": "review-002",
        "kind": "resolution_verification", "status": "failed", "new_material_findings": 1,
        "evidence_gap": "CHG-9006-R002 (class B)",
    }
    manifest_v2 = _manifest("CHG-9006", manifest_v1["review"]["iterations"] + [it2])
    provenance_v2 = _provenance("CHG-9006", provenance_v1["records"] + [
        _record("resolution-001", "resolution", a2, "chg-9006-resolution-001", "resolution-exec", "resolution-ctx",
                extra={"scope": ["src/x.py"], "targets": ["CHG-9006-R001"]}),
        _record("review-002", "review", a2, "chg-9006-resolution-001", "review-exec-2", "review-ctx-2"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v2, provenance_v2, "resolution 1 verification: still failing")

    a3 = _freeze_commit(root, {"src/x.py": "v3\n"}, "resolution 2")
    it3 = {
        "id": "review-003", "revision": "chg-9006-resolution-002",
        "subject_provenance": "resolution-002", "reviewer_provenance": "review-003",
        "kind": "resolution_verification", "status": "failed", "new_material_findings": 1,
        "evidence_gap": "CHG-9006-R003 (class B)",
    }
    manifest_v3 = _manifest("CHG-9006", manifest_v2["review"]["iterations"] + [it3])
    provenance_v3 = _provenance("CHG-9006", provenance_v2["records"] + [
        _record("resolution-002", "resolution", a3, "chg-9006-resolution-002", "resolution-exec-2", "resolution-ctx-2",
                extra={"scope": ["src/x.py"], "targets": ["CHG-9006-R002"]}),
        _record("review-003", "review", a3, "chg-9006-resolution-002", "review-exec-3", "review-ctx-3"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v3, provenance_v3, "resolution 2 verification: still failing")
    return manifest_v3, provenance_v3, a3


def test_convergence_limit_blocks_without_declared_failed_state(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    change_dir = "CHG-9006-limit"
    manifest_v3, provenance_v3, a3 = _build_two_strike_manifest(root, change_dir)
    result = validate_project(root, resolve_protocol_root())
    assert not result.passed
    assert any("review_convergence_failed" in m for m in _messages(result))


def test_convergence_limit_blocks_further_resolution_verification_without_decision(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    change_dir = "CHG-9006-limit2"
    manifest_v3, provenance_v3, a3 = _build_two_strike_manifest(root, change_dir)

    a4 = _freeze_commit(root, {"src/x.py": "v4\n"}, "resolution 3 attempt without decision")
    it4 = {
        "id": "review-004", "revision": "chg-9006-resolution-003",
        "subject_provenance": "resolution-003", "reviewer_provenance": "review-004",
        "kind": "resolution_verification", "status": "passed",
    }
    manifest_v4 = _manifest(
        "CHG-9006", manifest_v3["review"]["iterations"] + [it4], top_status="passed",
        convergence={"state": "review_convergence_failed", "consecutive_unconverged_verifications": 2},
    )
    provenance_v4 = _provenance("CHG-9006", provenance_v3["records"] + [
        _record("resolution-003", "resolution", a4, "chg-9006-resolution-003", "resolution-exec-3", "resolution-ctx-3",
                extra={"scope": ["src/x.py"], "targets": ["CHG-9006-R003"]}),
        _record("review-004", "review", a4, "chg-9006-resolution-003", "review-exec-4", "review-ctx-4"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v4, provenance_v4, "illegal continuation")

    result = validate_project(root, resolve_protocol_root())
    assert not result.passed
    messages = _messages(result)
    assert any("requires its own valid convergence_decision" in m for m in messages)
    assert any("further resolution_verification Iteration is not valid" in m for m in messages)


def test_convergence_limit_allows_new_initial_review_after_decision(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    change_dir = "CHG-9006-limit3"
    manifest_v3, provenance_v3, a3 = _build_two_strike_manifest(root, change_dir)

    a4 = _freeze_commit(root, {"src/x.py": "v4 full rewrite\n"}, "engineer-authorized full review subject")
    it4 = {
        "id": "review-004", "revision": "chg-9006-fullreview-001",
        "subject_provenance": "fullreview-001", "reviewer_provenance": "review-004",
        "kind": "initial_review", "status": "passed",
        # CHG-0011-R001 fix: the decision lives on the specific Iteration it
        # authorizes, not a shared manifest-wide field.
        "convergence_decision": {
            "option": "new_full_review",
            "reason": "Two consecutive scoped Resolution Verifications produced independent material findings; engineer authorized a fresh unrestricted Initial Review.",
            "recorded_at": "2026-08-17T01:00:00Z",
        },
    }
    manifest_v4 = _manifest(
        "CHG-9006", manifest_v3["review"]["iterations"] + [it4], top_status="passed",
        # Trailing Core-derived state after this new initial_review Iteration
        # is nominal/0 again (FR-011): only the counter/state track current
        # trailing reality; the decision itself is per-Iteration, permanent
        # history (INV-003 still applies to the counter/state fields).
        convergence={"state": "nominal", "consecutive_unconverged_verifications": 0},
    )
    provenance_v4 = _provenance("CHG-9006", provenance_v3["records"] + [
        _record("fullreview-001", "implementation", a4, "chg-9006-fullreview-001", "fullreview-exec", "fullreview-ctx"),
        _record("review-004", "review", a4, "chg-9006-fullreview-001", "review-exec-4", "review-ctx-4"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v4, provenance_v4, "legitimate full review escalation")

    result = validate_project(root, resolve_protocol_root())
    assert result.passed, _messages(result)


def test_convergence_decision_cannot_be_reused_across_independent_episodes(tmp_path: Path) -> None:
    """CHG-0011-R001 (BLOCKER, found by independent Strict Review Iteration 1):

    a decision recorded for one Non-Convergence episode must not silently
    authorize a second, later, fully independent episode. Reproduces the
    exact scenario from review.md's CHG-0011-R001: episode 1 legitimately
    resolved with a valid decision and a following initial_review that
    itself fails with an unrelated finding, then episode 2 (a fresh
    Resolution -> two more consecutive resolution_verification failures)
    occurs, then a final initial_review is marked passed while carrying no
    convergence_decision of its own.
    """
    root = tmp_path
    _init_repo(root)
    change_dir = "CHG-9006-reuse"
    manifest_v3, provenance_v3, a3 = _build_two_strike_manifest(root, change_dir)

    # Episode 1: resolved with a valid decision; the following initial_review
    # itself fails on a fresh, unrelated (non-convergence-counting) finding.
    a4 = _freeze_commit(root, {"src/x.py": "v4 full rewrite\n"}, "full review after episode 1")
    it4 = {
        "id": "review-004", "revision": "chg-9006-fullreview-001",
        "subject_provenance": "fullreview-001", "reviewer_provenance": "review-004",
        "kind": "initial_review", "status": "failed",
        "convergence_decision": {"option": "new_full_review", "reason": "Episode 1 authorization."},
        "evidence_gap": "unrelated finding, not itself a convergence-counting resolution_verification failure",
    }
    manifest_v4 = _manifest("CHG-9006", manifest_v3["review"]["iterations"] + [it4],
                             convergence={"state": "nominal", "consecutive_unconverged_verifications": 0})
    provenance_v4 = _provenance("CHG-9006", provenance_v3["records"] + [
        _record("fullreview-001", "implementation", a4, "chg-9006-fullreview-001", "fullreview-exec", "fullreview-ctx"),
        _record("review-004", "review", a4, "chg-9006-fullreview-001", "review-exec-4", "review-ctx-4"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v4, provenance_v4, "episode 1 full review, still failing")

    # Episode 2: an entirely new, independent two-strike streak.
    a5 = _freeze_commit(root, {"src/x.py": "v5\n"}, "resolution episode-2 attempt 1")
    it5 = {
        "id": "review-005", "revision": "chg-9006-resolution-010",
        "subject_provenance": "resolution-010", "reviewer_provenance": "review-005",
        "kind": "resolution_verification", "status": "failed", "new_material_findings": 1,
        "evidence_gap": "episode 2, strike 1",
    }
    manifest_v5 = _manifest("CHG-9006", manifest_v4["review"]["iterations"] + [it5])
    provenance_v5 = _provenance("CHG-9006", provenance_v4["records"] + [
        _record("resolution-010", "resolution", a5, "chg-9006-resolution-010", "resolution-exec-10", "resolution-ctx-10",
                extra={"scope": ["src/x.py"], "targets": ["CHG-9006-R010"]}),
        _record("review-005", "review", a5, "chg-9006-resolution-010", "review-exec-5", "review-ctx-5"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v5, provenance_v5, "episode 2 strike 1")

    a6 = _freeze_commit(root, {"src/x.py": "v6\n"}, "resolution episode-2 attempt 2")
    it6 = {
        "id": "review-006", "revision": "chg-9006-resolution-011",
        "subject_provenance": "resolution-011", "reviewer_provenance": "review-006",
        "kind": "resolution_verification", "status": "failed", "new_material_findings": 1,
        "evidence_gap": "episode 2, strike 2",
    }
    manifest_v6 = _manifest("CHG-9006", manifest_v5["review"]["iterations"] + [it6])
    provenance_v6 = _provenance("CHG-9006", provenance_v5["records"] + [
        _record("resolution-011", "resolution", a6, "chg-9006-resolution-011", "resolution-exec-11", "resolution-ctx-11",
                extra={"scope": ["src/x.py"], "targets": ["CHG-9006-R011"]}),
        _record("review-006", "review", a6, "chg-9006-resolution-011", "review-exec-6", "review-ctx-6"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v6, provenance_v6, "episode 2 strike 2 -- second Non-Convergence episode")

    # Illegitimate: a new initial_review passed with NO convergence_decision
    # of its own for episode 2.
    a7 = _freeze_commit(root, {"src/x.py": "v7\n"}, "silent bypass attempt")
    it7 = {
        "id": "review-007", "revision": "chg-9006-fullreview-002",
        "subject_provenance": "fullreview-002", "reviewer_provenance": "review-007",
        "kind": "initial_review", "status": "passed",
    }
    manifest_v7 = _manifest("CHG-9006", manifest_v6["review"]["iterations"] + [it7], top_status="passed",
                             convergence={"state": "nominal", "consecutive_unconverged_verifications": 0})
    provenance_v7 = _provenance("CHG-9006", provenance_v6["records"] + [
        _record("fullreview-002", "implementation", a7, "chg-9006-fullreview-002", "fullreview-exec-2", "fullreview-ctx-2"),
        _record("review-007", "review", a7, "chg-9006-fullreview-002", "review-exec-7", "review-ctx-7"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v7, provenance_v7, "bypass attempt: no decision for episode 2")

    result = validate_project(root, resolve_protocol_root())
    assert not result.passed, "episode 2's Non-Convergence must require its own decision"
    assert any("requires its own valid convergence_decision" in m for m in _messages(result))


def test_accept_residual_risk_requires_project_policy_permission(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)  # default forge.yml: allow_residual_risk_acceptance absent -> not permitted
    change_dir = "CHG-9006-risk"
    manifest_v3, provenance_v3, a3 = _build_two_strike_manifest(root, change_dir)
    a4 = _freeze_commit(root, {"src/x.py": "v4\n"}, "accept residual risk attempt")
    it4 = {
        "id": "review-004", "revision": "chg-9006-fullreview-001",
        "subject_provenance": "fullreview-001", "reviewer_provenance": "review-004",
        "kind": "initial_review", "status": "passed",
        "convergence_decision": {"option": "accept_residual_risk", "reason": "Cost outweighs remaining risk."},
    }
    manifest_v4 = _manifest("CHG-9006", manifest_v3["review"]["iterations"] + [it4], top_status="passed",
                             convergence={"state": "nominal", "consecutive_unconverged_verifications": 0})
    provenance_v4 = _provenance("CHG-9006", provenance_v3["records"] + [
        _record("fullreview-001", "implementation", a4, "chg-9006-fullreview-001", "fullreview-exec", "fullreview-ctx"),
        _record("review-004", "review", a4, "chg-9006-fullreview-001", "review-exec-4", "review-ctx-4"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v4, provenance_v4, "record decision without policy permission")

    result = validate_project(root, resolve_protocol_root())
    assert not result.passed
    assert any("explicitly permit it" in m for m in _messages(result))


def test_accept_residual_risk_permitted_by_project_policy(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root, forge_yml=FORGE_YML_ALLOW_RESIDUAL_RISK)
    change_dir = "CHG-9006-risk-ok"
    manifest_v3, provenance_v3, a3 = _build_two_strike_manifest(root, change_dir)
    a4 = _freeze_commit(root, {"src/x.py": "v4\n"}, "accept residual risk, permitted")
    it4 = {
        "id": "review-004", "revision": "chg-9006-fullreview-001",
        "subject_provenance": "fullreview-001", "reviewer_provenance": "review-004",
        "kind": "initial_review", "status": "passed",
        "convergence_decision": {"option": "accept_residual_risk", "reason": "Cost outweighs remaining risk; documented and approved."},
    }
    manifest_v4 = _manifest("CHG-9006", manifest_v3["review"]["iterations"] + [it4], top_status="passed",
                             convergence={"state": "nominal", "consecutive_unconverged_verifications": 0})
    provenance_v4 = _provenance("CHG-9006", provenance_v3["records"] + [
        _record("fullreview-001", "implementation", a4, "chg-9006-fullreview-001", "fullreview-exec", "fullreview-ctx"),
        _record("review-004", "review", a4, "chg-9006-fullreview-001", "review-exec-4", "review-ctx-4"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v4, provenance_v4, "record decision with policy permission")

    result = validate_project(root, resolve_protocol_root())
    assert result.passed, _messages(result)


def test_resolution_scope_wildcard_does_not_bypass_containment(tmp_path: Path) -> None:
    """CHG-0011-R003 (MAJOR, found by independent Strict Review Iteration 1):
    a broad glob like scope: ["*"] must not cover paths it was never meant
    to. Scope is exact-path-only; this proves a wildcard is simply a literal
    string that matches nothing real, not a pattern that swallows the delta.
    """
    root, change_dir, manifest_v1, a1, a2, resolution_record = _out_of_scope_setup(tmp_path)
    resolution_record["scope"] = ["*"]
    manifest_v2 = _manifest("CHG-9002", manifest_v1["review"]["iterations"] + [{
        "id": "review-002", "revision": "chg-9002-resolution-001",
        "subject_provenance": "resolution-001", "reviewer_provenance": "review-002",
        "kind": "resolution_verification", "status": "passed",
    }], top_status="passed")
    provenance_v2 = _provenance("CHG-9002", [
        _impl_record(a1, "chg-9002-impl-001"), resolution_record,
        _record("review-002", "review", a2, "chg-9002-resolution-001", "review-exec-2", "review-ctx-2"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v2, provenance_v2, "wildcard scope bypass attempt")

    result = validate_project(root, resolve_protocol_root())
    assert not result.passed
    assert any("Out-of-Scope Mutation" in m for m in _messages(result))


# ---------------------------------------------------------------------------
# TDD-014 — a recurring unresolved original finding (class A) does not, by
# itself, increment the convergence counter.
# ---------------------------------------------------------------------------

def test_recurring_unresolved_finding_does_not_increment_convergence(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    change_dir = "CHG-9007-classA"
    a1 = _freeze_commit(root, {"src/x.py": "v1\n"}, "implementation")
    manifest_v1 = _manifest("CHG-9007", [{
        "id": "review-001", "revision": "chg-9007-impl-001",
        "subject_provenance": "impl-001", "status": "failed",
    }])
    provenance_v1 = _provenance("CHG-9007", [_record("impl-001", "implementation", a1, "chg-9007-impl-001", "impl-exec", "impl-ctx")])
    _write_metadata_commit(root, change_dir, manifest_v1, provenance_v1, "freeze")

    a2 = _freeze_commit(root, {"src/x.py": "v1 unchanged fix attempt\n"}, "incomplete resolution 1")
    it2 = {
        "id": "review-002", "revision": "chg-9007-resolution-001",
        "subject_provenance": "resolution-001", "reviewer_provenance": "review-002",
        "kind": "resolution_verification", "status": "failed", "new_material_findings": 0,
        "evidence_gap": "CHG-9007-R001 (class A): still unresolved",
    }
    manifest_v2 = _manifest("CHG-9007", manifest_v1["review"]["iterations"] + [it2])
    provenance_v2 = _provenance("CHG-9007", provenance_v1["records"] + [
        _record("resolution-001", "resolution", a2, "chg-9007-resolution-001", "resolution-exec", "resolution-ctx",
                extra={"scope": ["src/x.py"], "targets": ["CHG-9007-R001"]}),
        _record("review-002", "review", a2, "chg-9007-resolution-001", "review-exec-2", "review-ctx-2"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v2, provenance_v2, "resolution 1 still incomplete")

    a3 = _freeze_commit(root, {"src/x.py": "v1 still unchanged\n"}, "incomplete resolution 2")
    it3 = {
        "id": "review-003", "revision": "chg-9007-resolution-002",
        "subject_provenance": "resolution-002", "reviewer_provenance": "review-003",
        "kind": "resolution_verification", "status": "failed", "new_material_findings": 0,
        "evidence_gap": "CHG-9007-R001 (class A): still unresolved",
    }
    manifest_v3 = _manifest("CHG-9007", manifest_v2["review"]["iterations"] + [it3])
    provenance_v3 = _provenance("CHG-9007", provenance_v2["records"] + [
        _record("resolution-002", "resolution", a3, "chg-9007-resolution-002", "resolution-exec-2", "resolution-ctx-2",
                extra={"scope": ["src/x.py"], "targets": ["CHG-9007-R001"]}),
        _record("review-003", "review", a3, "chg-9007-resolution-002", "review-exec-3", "review-ctx-3"),
    ])
    _write_metadata_commit(root, change_dir, manifest_v3, provenance_v3, "resolution 2 still incomplete")

    result = validate_project(root, resolve_protocol_root())
    # Two consecutive failures, but new_material_findings is 0 both times: no
    # Convergence Limit finding should appear.
    assert not any("Convergence Limit" in m or "review_convergence_failed" in m for m in _messages(result))
