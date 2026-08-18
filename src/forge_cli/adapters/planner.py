"""Deterministic Harness-agnostic Adapter planning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from forge_cli.adapters.capabilities import (
    CapabilityLimitation,
    CapabilityRequirement,
    evaluate_capability_requirements,
)
from forge_cli.adapters.manifest import AdapterManifest, require_protocol_compatibility
from forge_cli.adapters.ownership import classify_artifact
from forge_cli.adapters.plan import (
    AdapterOperation,
    AdapterPlan,
    OperationIntent,
    OwnershipMode,
    digest_content,
)
from forge_cli.adapters.state import GeneratedArtifact


@dataclass(frozen=True)
class EffectiveAdapterConfiguration:
    project_protocol: int
    capability_requirements: tuple[CapabilityRequirement, ...]

    def __init__(
        self,
        project_protocol: int,
        capability_requirements: Iterable[CapabilityRequirement],
    ) -> None:
        object.__setattr__(self, "project_protocol", project_protocol)
        object.__setattr__(self, "capability_requirements", tuple(capability_requirements))


@dataclass(frozen=True)
class ProjectedArtifact:
    path: str
    ownership: OwnershipMode
    content: str
    merge_result: str | None = None
    merge_strategy_id: str | None = None


@dataclass(frozen=True)
class RepositoryArtifactState:
    path: str
    exists: bool
    current_digest: str | None
    expected_digest: str | None


def _limitation_text(limitation) -> str:
    return (
        f"{limitation.requirement_id}: capability {limitation.capability} "
        f"cannot be enforced ({limitation.source_reference})"
    )


def plan_adapter(
    *,
    manifest: AdapterManifest,
    effective_configuration: EffectiveAdapterConfiguration,
    projections: Iterable[ProjectedArtifact],
    repository_state: Iterable[RepositoryArtifactState],
    additional_limitations: Iterable[CapabilityLimitation] = (),
    previous_generated: Iterable[GeneratedArtifact] = (),
) -> AdapterPlan:
    """Produce a stable plan from already-resolved Forge and Adapter inputs."""
    require_protocol_compatibility(manifest, effective_configuration.project_protocol)

    capability_limitations = evaluate_capability_requirements(
        declared_capabilities=manifest.capabilities,
        requirements=effective_configuration.capability_requirements,
    )
    limitations = (*capability_limitations, *additional_limitations)

    states: dict[str, RepositoryArtifactState] = {}
    for state in repository_state:
        if state.path in states:
            raise ValueError(f"Duplicate repository state for path: {state.path}")
        states[state.path] = state

    projected_by_path: dict[str, ProjectedArtifact] = {}
    for projection in projections:
        if projection.path in projected_by_path:
            raise ValueError(f"Duplicate projected artifact path: {projection.path}")
        projected_by_path[projection.path] = projection

    previous_by_path: dict[str, GeneratedArtifact] = {}
    for artifact in previous_generated:
        if artifact.path in previous_by_path:
            raise ValueError(f"Duplicate previous generated artifact path: {artifact.path}")
        previous_by_path[artifact.path] = artifact

    operations: list[AdapterOperation] = []
    conflicts: list[str] = []

    for path in sorted(projected_by_path):
        projection = projected_by_path[path]
        state = states.get(
            path,
            RepositoryArtifactState(
                path=path,
                exists=False,
                current_digest=None,
                expected_digest=None,
            ),
        )

        merge_is_proven = (
            projection.ownership is OwnershipMode.SHARED
            and projection.merge_result is not None
            and bool(projection.merge_strategy_id)
        )
        merge_result = projection.merge_result if merge_is_proven else None

        decision = classify_artifact(
            ownership=projection.ownership,
            exists=state.exists,
            current_digest=state.current_digest,
            expected_digest=state.expected_digest,
            merge_result=merge_result,
            desired_digest=digest_content(projection.content),
        )

        operation_content = decision.content if decision.content is not None else projection.content
        expected_current_digest = (
            state.current_digest
            if decision.intent in {OperationIntent.UPDATE, OperationIntent.UNCHANGED}
            and state.exists
            else None
        )
        operations.append(
            AdapterOperation.from_content(
                path=path,
                ownership=projection.ownership,
                intent=decision.intent,
                content=operation_content,
                expected_current_digest=expected_current_digest,
            )
        )

        if decision.intent is OperationIntent.CONFLICT:
            if projection.ownership is OwnershipMode.SHARED and projection.merge_result is not None and not projection.merge_strategy_id:
                conflicts.append(f"{path}: shared merge result lacks deterministic merge strategy identity")
            else:
                conflicts.append(f"{path}: ownership or expected-state conflict")

    for path in sorted(previous_by_path.keys() - projected_by_path.keys()):
        previous = previous_by_path[path]
        state = states.get(
            path,
            RepositoryArtifactState(
                path=path,
                exists=False,
                current_digest=None,
                expected_digest=None,
            ),
        )
        if (
            state.exists
            and state.expected_digest == previous.digest
            and state.current_digest == state.expected_digest
        ):
            operations.append(
                AdapterOperation(
                    path=path,
                    ownership=OwnershipMode.FORGE_OWNED,
                    intent=OperationIntent.DELETE_GENERATED,
                    content_digest=previous.digest,
                    expected_current_digest=previous.digest,
                )
            )
            continue

        operations.append(
            AdapterOperation(
                path=path,
                ownership=OwnershipMode.FORGE_OWNED,
                intent=OperationIntent.CONFLICT,
                content_digest=previous.digest,
            )
        )
        conflicts.append(f"{path}: ownership or expected-state conflict")

    return AdapterPlan(
        adapter_id=manifest.adapter_id,
        operations=operations,
        limitations=sorted(_limitation_text(item) for item in limitations),
        conflicts=sorted(conflicts),
    )
