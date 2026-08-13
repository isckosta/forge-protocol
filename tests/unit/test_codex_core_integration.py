from __future__ import annotations

from hashlib import sha256

from forge_cli.adapters.capabilities import CapabilityRequirement, RequirementSource
from forge_cli.adapters.ownership import DriftKind
from forge_cli.adapters.plan import OperationIntent, OwnershipMode
from forge_cli.adapters.planner import RepositoryArtifactState
from forge_cli.adapters.codex import load_codex_adapter_descriptor
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


def _bundle():
    return generate_codex_projection_bundle(
        CodexProjectionInput(
            flow_id="full",
            flow_content="stages: [verification, strict_review]",
            contract_content="canonical contract",
        )
    )


def test_bundle_resources_become_forge_owned_generic_operations() -> None:
    _require_behavior()
    target = resolve_publication_target(explicit_target="tools/codex")
    assert target is not None
    plan = plan_codex_projection(
        bundle=_bundle(), target=target, project_protocol=1,
        capability_requirements=(), repository_state=(),
    )
    assert [item.path for item in plan.operations] == [
        "tools/codex/forge-contract.md", "tools/codex/forge-flow.md",
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
                path="tools/codex/forge-flow.md", exists=True,
                current_digest="user-state", expected_digest=None,
            ),
        ),
    )
    operation = next(item for item in plan.operations if item.path.endswith("forge-flow.md"))
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


def test_installation_record_uses_forge_owned_planned_artifacts() -> None:
    _require_behavior()
    descriptor = load_codex_adapter_descriptor()
    target = resolve_publication_target(explicit_target="tools/codex")
    assert target is not None
    plan = plan_codex_projection(
        bundle=_bundle(), target=target, project_protocol=1,
        capability_requirements=(), repository_state=(),
    )
    record = build_codex_installation_record(descriptor=descriptor, plan=plan)
    assert record.adapter_id == "codex"
    assert [item.path for item in record.generated_artifacts] == [
        "tools/codex/forge-contract.md", "tools/codex/forge-flow.md",
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
    record = build_codex_installation_record(descriptor=descriptor, plan=plan)
    observed = {item.path: item.digest for item in record.generated_artifacts}
    changed_path = record.generated_artifacts[0].path
    observed[changed_path] = sha256(b"changed").hexdigest()
    findings = detect_codex_drift(record=record, observed_digests=observed)
    assert len(findings) == 1
    assert findings[0].path == changed_path
    assert findings[0].kind is DriftKind.MODIFIED
