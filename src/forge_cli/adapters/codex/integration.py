from __future__ import annotations

from typing import Iterable, Mapping

from forge_cli.adapters.capabilities import CapabilityLimitation, CapabilityRequirement
from forge_cli.adapters.ownership import GeneratedDrift, detect_generated_drift
from forge_cli.adapters.plan import AdapterPlan, OperationIntent, OwnershipMode
from forge_cli.adapters.planner import (
    EffectiveAdapterConfiguration,
    ProjectedArtifact,
    RepositoryArtifactState,
    plan_adapter,
)
from forge_cli.adapters.state import (
    AdapterInstallationRecord,
    GeneratedArtifact,
)
from forge_cli.adapters.codex import CodexAdapterDescriptor
from forge_cli.adapters.codex.projection import CodexProjectionBundle
from forge_cli.adapters.codex.targets import PublicationTarget, resolve_resource_path


def plan_codex_projection(
    *,
    bundle: CodexProjectionBundle,
    target: PublicationTarget,
    project_protocol: int,
    capability_requirements: Iterable[CapabilityRequirement],
    repository_state: Iterable[RepositoryArtifactState],
    invariant_limitations: Iterable[CapabilityLimitation] = (),
) -> AdapterPlan:
    from forge_cli.adapters.codex import load_codex_adapter_descriptor

    descriptor = load_codex_adapter_descriptor()
    projections = tuple(
        ProjectedArtifact(
            path=resolve_resource_path(target, resource.name),
            ownership=OwnershipMode.FORGE_OWNED,
            content=resource.content,
        )
        for resource in bundle.resources
    )
    return plan_adapter(
        manifest=descriptor.manifest,
        effective_configuration=EffectiveAdapterConfiguration(
            project_protocol=project_protocol,
            capability_requirements=capability_requirements,
        ),
        projections=projections,
        repository_state=repository_state,
        additional_limitations=invariant_limitations,
    )


def build_codex_installation_record(
    *,
    descriptor: CodexAdapterDescriptor,
    plan: AdapterPlan,
) -> AdapterInstallationRecord:
    generated = (
        GeneratedArtifact(path=operation.path, digest=operation.content_digest)
        for operation in plan.operations
        if operation.ownership is OwnershipMode.FORGE_OWNED
        and operation.intent in {OperationIntent.CREATE, OperationIntent.UPDATE}
    )
    manifest = descriptor.manifest
    return AdapterInstallationRecord(
        adapter_id=manifest.adapter_id,
        adapter_version=manifest.version,
        harness=manifest.harness,
        protocol_min=manifest.protocol_min,
        protocol_max_exclusive=manifest.protocol_max_exclusive,
        generated_artifacts=generated,
        limitations=plan.limitations,
    )


def detect_codex_drift(
    *,
    record: AdapterInstallationRecord,
    observed_digests: Mapping[str, str | None],
) -> tuple[GeneratedDrift, ...]:
    return detect_generated_drift(record, observed_digests)
