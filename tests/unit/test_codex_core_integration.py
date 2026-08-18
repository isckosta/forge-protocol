from __future__ import annotations

from hashlib import sha256

from forge_cli.adapters.capabilities import CapabilityRequirement, RequirementSource
from forge_cli.adapters.ownership import DriftKind
from forge_cli.adapters.plan import OperationIntent, OwnershipMode
from forge_cli.adapters.planner import RepositoryArtifactState
from forge_cli.adapters.codex import load_codex_adapter_descriptor
from forge_cli.adapters.codex.assessment import assess_invariant, to_generic_limitation
from forge_cli.adapters.codex.projection import CodexProjectionInput, generate_codex_projection_bundle
from forge_cli.adapters.codex.targets import resolve_publication_target

try:
    from forge_cli.adapters.codex.integration import (
        build_codex_installation_record,
        detect_codex_drift,
        plan_codex_projection,
    )
except ImportError:
    build_codex_installation_record = None
    detect_codex_drift = None
    plan_codex_projection = None


def _require_behavior() -> None:
    assert plan_codex_projection is not None, "Codex Core integration is not implemented yet"
    assert build_codex_installation_record is not None
    assert detect_codex_drift is not None


def _bundle(flow_id: str = "full", protocol_id: int = 1):
    return generate_codex_projection_bundle(
        CodexProjectionInput(
            flow_id=flow_id,
            flow_content="stages: [verification, strict_review]",
            contract_content="canonical contract",
            protocol_id=protocol_id,
        )
    )


def test_protocol1_projection_does_not_retroactively_project_protocol2_provenance() -> None:
    bundle = _bundle("full", protocol_id=1)
    skill_resource = next(item for item in bundle.resources if item.name == "SKILL.md")

    assert "provenance.yml" not in skill_resource.content
    assert "subject_provenance" not in skill_resource.content


def test_protocol2_all_flows_projection_require_review_provenance_boundary() -> None:
    for flow_id in ("fast", "standard", "full"):
        bundle = _bundle(flow_id, protocol_id=2)
        skill_resource = next(item for item in bundle.resources if item.name == "SKILL.md")
        assert "Execution and Execution Context independent" in skill_resource.content
        assert "changing Role inside the same conversation" in skill_resource.content
        assert "provenance.yml" in skill_resource.content
        assert "subject_provenance" in skill_resource.content
        assert "reviewer_provenance" in skill_resource.content
        assert "claimed" in skill_resource.content
        assert "recorded" in skill_resource.content
        assert "self-review" in skill_resource.content.lower()


def test_bundle_resources_become_forge_owned_generic_operations() -> None:
    _require_behavior()
    target = resolve_publication_target(explicit_target="tools/codex")
    assert target is not None
    plan = plan_codex_projection(
        bundle=_bundle(), target=target, project_protocol=1,
        capability_requirements=(), repository_state=(),
    )
    assert [item.path for item in plan.operations] == [
        "tools/codex/SKILL.md",
        "tools/codex/references/engineering-contract.md",
        "tools/codex/references/flows/full.yml",
    ]
    assert all(item.ownership is OwnershipMode.FORGE_OWNED for item in plan.operations)
    assert all(item.intent is OperationIntent.CREATE for item in plan.operations)


def test_existing_unowned_target_is_classified_as_conflict() -> None:
    _require_behavior()
    target = resolve_publication_target(explicit_target="tools/codex")
    assert target is not None
    plan = plan_codex_projection(
        bundle=_bundle(), target=target, project_protocol=1,
        capability_requirements=(),
        repository_state=(
            RepositoryArtifactState(
                path="tools/codex/references/flows/full.yml", exists=True,
                current_digest="user-state", expected_digest=None,
            ),
        ),
    )
    operation = next(item for item in plan.operations if item.path.endswith("references/flows/full.yml"))
    assert operation.intent is OperationIntent.CONFLICT
    assert plan.conflicts


def test_generic_capability_limitation_survives_codex_planning() -> None:
    _require_behavior()
    target = resolve_publication_target(explicit_target="tools/codex")
    assert target is not None
    requirement = CapabilityRequirement(
        requirement_id="requires-hooks", capability="hooks",
        source=RequirementSource.FORGE, source_reference="INV-HOOK",
    )
    plan = plan_codex_projection(
        bundle=_bundle(), target=target, project_protocol=1,
        capability_requirements=(requirement,), repository_state=(),
    )
    assert any("requires-hooks" in item for item in plan.limitations)


def test_represented_invariant_limitation_survives_plan_and_installation_record() -> None:
    _require_behavior()
    assessment = assess_invariant(
        invariant_id="INV-TDD",
        source_reference="FR-016",
        represented=True,
        technical_enforcement=False,
    )
    limitation = to_generic_limitation(assessment, capability="skills")
    assert limitation is not None
    target = resolve_publication_target(explicit_target="tools/codex")
    assert target is not None

    plan = plan_codex_projection(
        bundle=_bundle(),
        target=target,
        project_protocol=1,
        capability_requirements=(),
        invariant_limitations=(limitation,),
        repository_state=(),
    )
    record = build_codex_installation_record(
        descriptor=load_codex_adapter_descriptor(),
        plan=plan,
        target=target,
    )
    expected = ("INV-TDD: capability skills cannot be enforced (FR-016)",)

    assert plan.limitations == expected
    assert record.limitations == expected


def test_installation_record_uses_forge_owned_planned_artifacts() -> None:
    _require_behavior()
    descriptor = load_codex_adapter_descriptor()
    target = resolve_publication_target(explicit_target="tools/codex")
    assert target is not None
    plan = plan_codex_projection(
        bundle=_bundle(), target=target, project_protocol=1,
        capability_requirements=(), repository_state=(),
    )
    record = build_codex_installation_record(
        descriptor=descriptor,
        plan=plan,
        target=target,
    )
    assert record.adapter_id == "codex"
    assert [item.path for item in record.generated_artifacts] == [
        "tools/codex/SKILL.md",
        "tools/codex/references/engineering-contract.md",
        "tools/codex/references/flows/full.yml",
    ]
    assert [item.digest for item in record.generated_artifacts] == [
        item.content_digest for item in plan.operations
    ]


def test_recorded_generated_drift_reuses_generic_detection() -> None:
    _require_behavior()
    descriptor = load_codex_adapter_descriptor()
    target = resolve_publication_target(explicit_target="tools/codex")
    assert target is not None
    plan = plan_codex_projection(
        bundle=_bundle(), target=target, project_protocol=1,
        capability_requirements=(), repository_state=(),
    )
    record = build_codex_installation_record(
        descriptor=descriptor,
        plan=plan,
        target=target,
    )
    observed = {item.path: item.digest for item in record.generated_artifacts}
    changed_path = record.generated_artifacts[0].path
    observed[changed_path] = sha256(b"changed").hexdigest()
    findings = detect_codex_drift(record=record, observed_digests=observed)
    assert len(findings) == 1
    assert findings[0].path == changed_path
    assert findings[0].kind is DriftKind.MODIFIED
