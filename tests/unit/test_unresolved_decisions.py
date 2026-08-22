"""CHG-0013: Unresolved Decision Management mechanical validation slice.

Unlike CHG-0011's Resolution Verification machinery, this mechanism is
manifest-shape-only (no Git history dependency): `decisions[]` is a
self-contained, Core-derivable check against already-loaded YAML. Fixtures
therefore need no real Git repository, matching the Test Strategy's own
stated rationale (`test-strategy.md`).
"""
from __future__ import annotations

from pathlib import Path

import yaml

from forge_cli.protocol_resources import resolve_protocol_root
from forge_cli.validation import validate_project

FORGE_YML = """schema: forge/project@1
project:
  name: t
forge:
  protocol: 1
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


def _init(root: Path) -> None:
    forge = root / ".forge"
    forge.mkdir(parents=True)
    (forge / "forge.yml").write_text(FORGE_YML, encoding="utf-8")


def _init_protocol2(root: Path) -> None:
    _init(root)
    (root / ".forge/forge.yml").write_text(FORGE_YML.replace("protocol: 1", "protocol: 2"), encoding="utf-8")


def _write_manifest(root: Path, change_dir: str, manifest: dict) -> None:
    change = root / ".forge/changes" / change_dir
    change.mkdir(parents=True, exist_ok=True)
    (change / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def _base_manifest(decisions: list[dict], **overrides: object) -> dict:
    m: dict = {
        "schema": "forge/change@1",
        "change": {"id": "CHG-9101", "title": "T", "kind": "feature"},
        "flow": {"initial": "full", "current": "full"},
        "state": {"current": "tasks"},
        "artifacts": {},
        "tdd": {"status": "pending"},
        "verification": {"status": "pending"},
        "review": {"status": "pending", "blockers": 0, "majors": 0, "minors": 0, "observations": 0},
        "documentation": {"impact_evaluated": False},
        "decisions": decisions,
    }
    m.update(overrides)
    return m


def _messages(result) -> list[str]:
    return [f.message for f in result.findings]


PROTOCOL_ROOT = resolve_protocol_root()


# ---------------------------------------------------------------------------
# TDD-001 — legacy manifests (this repository's own real Changes) are
# unaffected: none declares `decisions`, so none produces a finding from
# this Change's new logic.
# ---------------------------------------------------------------------------

def test_legacy_manifests_are_unaffected() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = validate_project(repo_root, resolve_protocol_root())
    offending = [m for m in _messages(result) if "Decision" in m or "decisions" in m]
    assert offending == [], offending


# ---------------------------------------------------------------------------
# TDD-002 — golden path: a resolved material Decision does not block.
# ---------------------------------------------------------------------------

def test_resolved_material_decision_does_not_block(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "specification",
        "discovered_in": "specification", "resolved_via": "human_decision",
    }
    manifest = _base_manifest(
        [decision],
        artifacts={"specification_review": "complete"},
        review={"status": "passed", "blockers": 0, "majors": 0, "minors": 0, "observations": 0},
    )
    _write_manifest(tmp_path, "CHG-9101-golden", manifest)

    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert result.passed, _messages(result)


# ---------------------------------------------------------------------------
# TDD-003 — Open-blocking status conflicts with an already-passed Gate.
# ---------------------------------------------------------------------------

def _conflict_manifest(status: str) -> dict:
    decision = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": status, "authority": "human", "owning_artifact": "specification",
        "discovered_in": "specification",
    }
    return _base_manifest([decision], artifacts={"specification_review": "complete"})


def test_open_blocking_status_conflicts_with_passed_gate(tmp_path: Path) -> None:
    for status in ("open", "analyzing", "awaiting_decision"):
        root = tmp_path / status
        _init(root)
        _write_manifest(root, "CHG-9102-conflict", _conflict_manifest(status))
        result = validate_project(root, PROTOCOL_ROOT)
        assert not result.passed, status
        assert any("specification_review_passed" in m and "DEC-001" in m for m in _messages(result)), (status, _messages(result))


# ---------------------------------------------------------------------------
# TDD-004 — resolved and superseded entries never block (regression test for
# the defect Adversarial Specification Review caught before Architecture).
# ---------------------------------------------------------------------------

def test_superseded_decision_does_not_block(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": "superseded", "authority": "human", "owning_artifact": "specification",
        "discovered_in": "specification", "resolved_via": "human_decision",
    }
    manifest = _base_manifest([decision], artifacts={"specification_review": "complete"})
    _write_manifest(tmp_path, "CHG-9103-superseded", manifest)

    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert result.passed, _messages(result)


# ---------------------------------------------------------------------------
# TDD-005 — human-authority Decision cannot be resolved autonomously
# (C-055); Evidence Resolution remains allowed regardless of authority.
# ---------------------------------------------------------------------------

def test_human_authority_cannot_be_resolved_autonomously(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "specification",
        "discovered_in": "specification", "resolved_via": "autonomous_decision",
    }
    _write_manifest(tmp_path, "CHG-9104-c055", _base_manifest([decision]))

    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert not result.passed
    assert any("MUST NOT be resolved via autonomous_decision" in m for m in _messages(result))


def test_human_authority_evidence_resolution_is_allowed(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "specification",
        "discovered_in": "specification", "resolved_via": "evidence",
    }
    _write_manifest(tmp_path, "CHG-9105-evidence", _base_manifest([decision]))

    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert result.passed, _messages(result)


# ---------------------------------------------------------------------------
# CHG-0025 TDD-001 — an active approved Plan needs an explicit human act.
# ---------------------------------------------------------------------------

def _approved_plan_manifest(decisions: list[dict] | None = None, *, state: str = "tasks", **overrides: object) -> dict:
    return _base_manifest(
        decisions or [],
        state={"current": state},
        artifacts={"plan": "approved"},
        **overrides,
    )


def _write_plan_confirmation(root: Path, change_dir: str) -> None:
    change = root / ".forge/changes" / change_dir
    change.mkdir(parents=True, exist_ok=True)
    change_id = "-".join(change_dir.split("-")[:2])
    (change / "plan.md").write_text(
        "<!-- forge:plan-approval-confirmation -->\n"
        "## Registro de aprovação\n\n"
        "<!-- forge:plan-approval-record -->\n"
        "Aprovação humana explícita foi recebida do operador.\n",
        encoding="utf-8",
    )
    (change / "provenance.yml").write_text(
        yaml.safe_dump(
            {
                "schema": "forge/execution-provenance@2",
                "change": change_id,
                "records": [{
                    "id": "implementation-001",
                    "role": "implementation",
                    "execution": {"id": "exec-001", "context_id": "context-001"},
                    "recorded_at": "2026-08-22T12:00:00Z",
                    "revision": {"id": "revision-001", "immutable_ref": {"type": "git_commit", "value": "0" * 40}},
                    "source": {
                        "assurance": "recorded",
                        "observed_by": "operator",
                        "reference": "plan.md#approval-record",
                        "statement": "Aprovação humana explícita foi recebida do operador.",
                    },
                }],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_active_approved_plan_without_human_authorization_is_a_finding(tmp_path: Path) -> None:
    _init(tmp_path)
    _write_manifest(tmp_path, "CHG-9110-plan-no-authorization", _approved_plan_manifest())

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert not result.passed
    assert any("Plan" in message and "authorization" in message for message in _messages(result))


def test_active_approved_plan_with_human_decision_passes_plan_check(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "technical", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "plan",
        "discovered_in": "plan", "resolved_via": "human_decision",
    }
    change_dir = "CHG-9111-plan-human-authorization"
    _write_manifest(
        tmp_path,
        change_dir,
        _approved_plan_manifest([decision], change={"id": "CHG-9111", "title": "T", "kind": "feature"}),
    )
    _write_plan_confirmation(tmp_path, change_dir)

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert result.passed, _messages(result)


def test_protocol2_active_approved_plan_uses_same_authorization_rule(tmp_path: Path) -> None:
    _init_protocol2(tmp_path)
    decision = {
        "id": "DEC-001", "class": "technical", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "plan",
        "discovered_in": "plan", "resolved_via": "human_decision",
    }
    manifest = _approved_plan_manifest(
        [decision], schema="forge/change@2", protocol=2,
        change={"id": "CHG-9113", "title": "T", "kind": "feature"},
    )
    change_dir = "CHG-9113-protocol2-plan"
    _write_manifest(tmp_path, change_dir, manifest)
    _write_plan_confirmation(tmp_path, change_dir)

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert result.passed, _messages(result)


def test_specification_gate_remains_technical_without_plan_authorization(tmp_path: Path) -> None:
    _init(tmp_path)
    manifest = _base_manifest(
        [],
        artifacts={"specification_gate_passed": "complete", "specification_review": "complete"},
    )
    _write_manifest(tmp_path, "CHG-9116-technical-specification-gate", manifest)

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert result.passed, _messages(result)


def test_active_approved_plan_without_recorded_confirmation_is_a_finding(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "technical", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "plan",
        "discovered_in": "plan", "resolved_via": "human_decision",
    }
    _write_manifest(tmp_path, "CHG-9112-plan-unrecorded", _approved_plan_manifest([decision]))

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert not result.passed
    assert any("plan.md and provenance.yml" in message for message in _messages(result))


def test_active_approved_plan_with_self_observed_confirmation_is_a_finding(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "technical", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "plan",
        "discovered_in": "plan", "resolved_via": "human_decision",
    }
    change_dir = "CHG-9115-plan-self-observed"
    _write_manifest(tmp_path, change_dir, _approved_plan_manifest([decision]))
    _write_plan_confirmation(tmp_path, change_dir)
    provenance_path = tmp_path / ".forge/changes" / change_dir / "provenance.yml"
    provenance = yaml.safe_load(provenance_path.read_text())
    provenance["records"][0]["source"]["observed_by"] = "self"
    provenance_path.write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert not result.passed
    assert any("authorization" in message for message in _messages(result))


def test_active_approved_plan_with_foreign_provenance_is_a_finding(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "technical", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "plan",
        "discovered_in": "plan", "resolved_via": "human_decision",
    }
    change_dir = "CHG-9117-plan-foreign-provenance"
    _write_manifest(tmp_path, change_dir, _approved_plan_manifest([decision]))
    _write_plan_confirmation(tmp_path, change_dir)
    provenance_path = tmp_path / ".forge/changes" / change_dir / "provenance.yml"
    provenance = yaml.safe_load(provenance_path.read_text())
    provenance["change"] = "CHG-9999"
    provenance_path.write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert not result.passed
    assert any("authorization" in message for message in _messages(result))


def test_active_approved_plan_with_malformed_plan_is_a_finding(tmp_path: Path) -> None:
    _init(tmp_path)
    _write_manifest(tmp_path, "CHG-9118-plan-malformed", _approved_plan_manifest())
    change = tmp_path / ".forge/changes/CHG-9118-plan-malformed"
    (change / "plan.md").write_bytes(b"\\xff\\xfe malformed")

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert not result.passed
    assert any("authorization" in message for message in _messages(result))


def test_active_approved_plan_with_multiple_approvals_is_ambiguous(tmp_path: Path) -> None:
    _init(tmp_path)
    def decision(number: int) -> dict:
        return {
            "id": f"DEC-{number:03d}", "class": "technical", "materiality": "material",
            "status": "resolved", "authority": "human", "owning_artifact": "plan",
            "discovered_in": "plan", "resolved_via": "human_decision",
        }
    _write_manifest(
        tmp_path,
        "CHG-9114-plan-ambiguous",
        _approved_plan_manifest([decision(1), decision(2)]),
    )

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert not result.passed
    assert any("ambiguous" in message for message in _messages(result))


def test_active_approved_plan_with_open_decision_fails_closed(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "technical", "materiality": "material",
        "status": "awaiting_decision", "authority": "human", "owning_artifact": "plan",
        "discovered_in": "plan",
    }
    _write_manifest(tmp_path, "CHG-9111-plan-open-authorization", _approved_plan_manifest([decision]))

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert not result.passed
    assert any("before_implementation" in message for message in _messages(result))


def test_active_approved_plan_with_autonomous_human_decision_fails_closed(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "technical", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "plan",
        "discovered_in": "plan", "resolved_via": "autonomous_decision",
    }
    _write_manifest(tmp_path, "CHG-9111-plan-autonomous-authorization", _approved_plan_manifest([decision]))

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert not result.passed
    assert any("C-055" in message for message in _messages(result))


def test_completed_approved_plan_without_new_authorization_remains_compatible(tmp_path: Path) -> None:
    _init(tmp_path)
    _write_manifest(
        tmp_path,
        "CHG-9112-plan-completed-compatibility",
        _approved_plan_manifest(state="complete"),
    )

    result = validate_project(tmp_path, PROTOCOL_ROOT)

    assert result.passed, _messages(result)


# ---------------------------------------------------------------------------
# TDD-006 — resolved_via <-> status consistency (FR-009).
# ---------------------------------------------------------------------------

def test_resolved_without_resolved_via_is_a_finding(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "technical", "materiality": "material",
        "status": "resolved", "authority": "agent", "owning_artifact": "tasks",
        "discovered_in": "tasks",
    }
    _write_manifest(tmp_path, "CHG-9106-noresolvedvia", _base_manifest([decision]))
    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert not result.passed
    assert any("declares no resolved_via" in m for m in _messages(result))


def test_resolved_via_without_resolved_status_is_a_finding(tmp_path: Path) -> None:
    _init(tmp_path)
    decision = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": "awaiting_decision", "authority": "human", "owning_artifact": "specification",
        "discovered_in": "specification", "resolved_via": "human_decision",
    }
    _write_manifest(tmp_path, "CHG-9107-premature", _base_manifest([decision]))
    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert not result.passed
    assert any("not yet resolved" in m for m in _messages(result))


# ---------------------------------------------------------------------------
# TDD-007 — malformed enum values (shape validation, adversarial matrix).
# ---------------------------------------------------------------------------

def _shape_case(**overrides: object) -> dict:
    base = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": "open", "authority": "human", "owning_artifact": "specification",
        "discovered_in": "specification",
    }
    base.update(overrides)
    return base


def test_malformed_fields_are_findings_without_raising(tmp_path: Path) -> None:
    cases = [
        _shape_case(**{"class": "product "}),
        _shape_case(**{"class": "PRODUCT"}),
        _shape_case(materiality=True),
        _shape_case(status="done"),
        _shape_case(authority="ai"),
        _shape_case(id="DEC-1"),
    ]
    for i, decision in enumerate(cases):
        root = tmp_path / f"case{i}"
        _init(root)
        _write_manifest(root, "CHG-9108-shape", _base_manifest([decision]))
        result = validate_project(root, PROTOCOL_ROOT)
        assert not result.passed, decision
        assert len(result.findings) >= 1


# ---------------------------------------------------------------------------
# TDD-008 — duplicate Decision id.
# ---------------------------------------------------------------------------

def test_duplicate_decision_id_is_a_finding(tmp_path: Path) -> None:
    _init(tmp_path)
    d1 = _shape_case()
    d2 = {**_shape_case(), "class": "technical", "owning_artifact": "tasks", "authority": "agent"}
    _write_manifest(tmp_path, "CHG-9109-dup", _base_manifest([d1, d2]))
    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert not result.passed
    assert any("Duplicate Decision id" in m for m in _messages(result))


# ---------------------------------------------------------------------------
# TDD-009 — owning_artifact inconsistent with Class (INV-003), both
# directions.
# ---------------------------------------------------------------------------

def test_owning_artifact_inconsistent_with_class(tmp_path: Path) -> None:
    escalated = {
        "id": "DEC-001", "class": "technical", "materiality": "material",
        "status": "open", "authority": "agent", "owning_artifact": "specification",
        "discovered_in": "tasks",
    }
    root1 = tmp_path / "escalated"
    _init(root1)
    _write_manifest(root1, "CHG-9110-escalated", _base_manifest([escalated]))
    result1 = validate_project(root1, PROTOCOL_ROOT)
    assert not result1.passed
    assert any("not a valid owning Artifact for class" in m for m in _messages(result1))

    late = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": "open", "authority": "human", "owning_artifact": "tasks",
        "discovered_in": "tasks",
    }
    root2 = tmp_path / "late"
    _init(root2)
    _write_manifest(root2, "CHG-9111-late", _base_manifest([late]))
    result2 = validate_project(root2, PROTOCOL_ROOT)
    assert not result2.passed
    assert any("not a valid owning Artifact for class" in m for m in _messages(result2))


# ---------------------------------------------------------------------------
# TDD-010 — invalidates referencing an artifact that never transitioned to
# `invalidated` (C-057).
# ---------------------------------------------------------------------------

def test_invalidates_target_still_complete_is_a_finding(tmp_path: Path) -> None:
    decision = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "specification",
        "discovered_in": "tasks", "resolved_via": "human_decision", "invalidates": ["tasks"],
    }
    root = tmp_path / "stale"
    _init(root)
    _write_manifest(root, "CHG-9112-stale", _base_manifest([decision], artifacts={"tasks": "complete"}))
    result = validate_project(root, PROTOCOL_ROOT)
    assert not result.passed
    assert any("must become invalidated until revisited" in m for m in _messages(result))

    root2 = tmp_path / "correct"
    _init(root2)
    _write_manifest(root2, "CHG-9113-correct", _base_manifest([decision], artifacts={"tasks": "invalidated"}))
    result2 = validate_project(root2, PROTOCOL_ROOT)
    assert result2.passed, _messages(result2)


# ---------------------------------------------------------------------------
# TDD-011 — non-material entries never trigger Gate-blocking findings,
# regardless of status.
# ---------------------------------------------------------------------------

def test_non_material_entry_never_blocks(tmp_path: Path) -> None:
    decision = {
        "id": "DEC-001", "class": "product", "materiality": "non_material",
        "status": "open", "authority": "human", "owning_artifact": "specification",
        "discovered_in": "specification",
    }
    _init(tmp_path)
    _write_manifest(tmp_path, "CHG-9114-nonmaterial", _base_manifest([decision], artifacts={"specification_review": "complete"}))
    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert result.passed, _messages(result)


# ---------------------------------------------------------------------------
# TDD-012 — absence of `decisions` (None and empty list) short-circuits.
# ---------------------------------------------------------------------------

def test_absent_or_empty_decisions_short_circuits(tmp_path: Path) -> None:
    root_none = tmp_path / "none"
    _init(root_none)
    manifest_none = _base_manifest([])
    del manifest_none["decisions"]
    _write_manifest(root_none, "CHG-9115-none", manifest_none)
    result_none = validate_project(root_none, PROTOCOL_ROOT)
    assert result_none.passed, _messages(result_none)

    root_empty = tmp_path / "empty"
    _init(root_empty)
    _write_manifest(root_empty, "CHG-9116-empty", _base_manifest([]))
    result_empty = validate_project(root_empty, PROTOCOL_ROOT)
    assert result_empty.passed, _messages(result_empty)


# ---------------------------------------------------------------------------
# CHG-0013-R002 (MAJOR, found by independent Strict Review Iteration 1):
# the human-authority floor for product/contract Classes (C-055, FR-017,
# authority_floor in protocol/policies/decision.yml) was only checked in
# the narrow combination authority == human AND resolved_via ==
# autonomous_decision. Setting authority directly to a non-human value on a
# product/contract Decision bypassed the floor entirely, defeating the one
# guarantee this Change's own Contract calls non-negotiable.
# ---------------------------------------------------------------------------

def test_product_class_below_human_authority_floor_is_a_finding(tmp_path: Path) -> None:
    decision = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": "resolved", "authority": "agent", "owning_artifact": "specification",
        "discovered_in": "specification", "resolved_via": "autonomous_decision",
    }
    _init(tmp_path)
    _write_manifest(tmp_path, "CHG-9117-r002-product", _base_manifest([decision]))
    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert not result.passed
    assert any("authority floor" in m for m in _messages(result))


def test_contract_class_below_human_authority_floor_is_a_finding(tmp_path: Path) -> None:
    decision = {
        "id": "DEC-001", "class": "contract", "materiality": "material",
        "status": "resolved", "authority": "agent_with_review", "owning_artifact": "specification",
        "discovered_in": "specification", "resolved_via": "autonomous_decision",
    }
    _init(tmp_path)
    _write_manifest(tmp_path, "CHG-9118-r002-contract", _base_manifest([decision]))
    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert not result.passed
    assert any("authority floor" in m for m in _messages(result))


# ---------------------------------------------------------------------------
# CHG-0021 TDD-004 — an invalid resolved_via message states the expected
# values, matching the owning_artifact message's existing convention
# (this exact branch had no prior test coverage).
# ---------------------------------------------------------------------------

def test_invalid_resolved_via_lists_expected_values(tmp_path: Path) -> None:
    decision = {
        "id": "DEC-001", "class": "technical", "materiality": "material",
        "status": "resolved", "authority": "agent", "owning_artifact": "tasks",
        "discovered_in": "tasks", "resolved_via": "explicit_human_act",
    }
    _init(tmp_path)
    _write_manifest(tmp_path, "CHG-9119-bad-resolved-via", _base_manifest([decision]))
    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert not result.passed
    messages = _messages(result)
    assert any("has an invalid resolved_via" in m for m in messages)
    assert any("expected one of" in m and "autonomous_decision" in m and "evidence" in m and "human_decision" in m for m in messages), messages


def test_architectural_and_technical_classes_are_not_floor_restricted(tmp_path: Path) -> None:
    decisions = [
        {
            "id": "DEC-001", "class": "architectural", "materiality": "material",
            "status": "resolved", "authority": "agent", "owning_artifact": "architecture",
            "discovered_in": "architecture", "resolved_via": "autonomous_decision",
        },
        {
            "id": "DEC-002", "class": "technical", "materiality": "material",
            "status": "resolved", "authority": "agent", "owning_artifact": "tasks",
            "discovered_in": "tasks", "resolved_via": "autonomous_decision",
        },
    ]
    _init(tmp_path)
    _write_manifest(tmp_path, "CHG-9119-r002-unrestricted", _base_manifest(decisions))
    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert result.passed, _messages(result)


# ---------------------------------------------------------------------------
# CHG-0013-R003 (MINOR, found by independent Strict Review Iteration 1):
# `invalidates` referencing an artifact key entirely absent from
# `artifacts` (as opposed to present-but-complete/approved) silently
# passed, because `artifacts.get(key)` returns None, which is not in
# {"complete","approved"}.
# ---------------------------------------------------------------------------

def test_invalidates_target_missing_from_artifacts_is_a_finding(tmp_path: Path) -> None:
    decision = {
        "id": "DEC-001", "class": "product", "materiality": "material",
        "status": "resolved", "authority": "human", "owning_artifact": "specification",
        "discovered_in": "tasks", "resolved_via": "human_decision", "invalidates": ["nonexistent_artifact_key"],
    }
    _init(tmp_path)
    _write_manifest(tmp_path, "CHG-9120-r003-missingkey", _base_manifest([decision], artifacts={}))
    result = validate_project(tmp_path, PROTOCOL_ROOT)
    assert not result.passed
    assert any("nonexistent_artifact_key" in m and "not tracked" in m for m in _messages(result))
