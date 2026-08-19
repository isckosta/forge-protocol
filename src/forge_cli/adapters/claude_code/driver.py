"""Claude Code implementation of the generic Harness Driver contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

import yaml

from forge_cli.adapters.assessment import assess_invariant, to_generic_limitation
from forge_cli.adapters.capabilities import CapabilityLimitation
from forge_cli.adapters.claude_code.descriptor import load_claude_code_adapter_descriptor
from forge_cli.adapters.claude_code.projection import generate_claude_code_skill_bundle
from forge_cli.adapters.claude_code.targets import (
    load_packaged_publication_target,
    validate_publication_root,
)
from forge_cli.adapters.driver import (
    AdapterProjection,
    AdapterProjectionContext,
)
from forge_cli.adapters.manifest import AdapterManifest
from forge_cli.adapters.plan import OwnershipMode
from forge_cli.adapters.planner import ProjectedArtifact
from forge_cli.adapters.validation import AdapterRepresentation


@dataclass(frozen=True)
class ClaudeCodeDriver:
    @property
    def manifest(self) -> AdapterManifest:
        return load_claude_code_adapter_descriptor().manifest

    @property
    def default_target(self) -> str | None:
        return load_packaged_publication_target()

    def validate_publication_root(self, publication_root: str) -> None:
        validate_publication_root(publication_root)

    def project(self, context: AdapterProjectionContext) -> AdapterProjection:
        bundle = generate_claude_code_skill_bundle(
            contract_content=context.contract_content,
            flows=context.flows,
            protocol_id=context.project_protocol,
            artifact_structure_content=context.artifact_structure_content,
            interaction_language=context.interaction_language,
        )
        stages, gates, has_tdd, has_strict_review = _flow_representation(context.flows)
        limitations = _limitations(
            has_tdd=has_tdd,
            has_strict_review=has_strict_review,
        )
        return AdapterProjection(
            artifacts=tuple(
                ProjectedArtifact(
                    path=(PurePosixPath(context.target) / resource.name).as_posix(),
                    ownership=OwnershipMode.FORGE_OWNED,
                    content=resource.content,
                )
                for resource in bundle.resources
            ),
            limitations=limitations,
            representation=AdapterRepresentation(
                stages=stages,
                gates=gates,
                represented_invariants=tuple(
                    invariant
                    for invariant, present in (
                        ("INV-001", True),
                        ("strict-review", has_strict_review),
                        ("tdd-red-before-behavior", has_tdd),
                    )
                    if present
                ),
                enforced_invariants=("INV-005",),
                limitations=limitations,
                repository_authority_preserved=True,
                red_before_behavior_preserved=has_tdd,
                strict_review_preserved=has_strict_review,
            ),
        )


def _flow_representation(
    flows: tuple[tuple[str, str], ...],
) -> tuple[tuple[str, ...], tuple[str, ...], bool, bool]:
    stages: set[str] = set()
    gates: set[str] = set()
    has_tdd = False
    has_strict_review = False
    for _, content in flows:
        data = yaml.safe_load(content) or {}
        for stage in data.get("stages") or ():
            stage_id = stage.get("id") if isinstance(stage, dict) else None
            if isinstance(stage_id, str):
                stages.add(stage_id)
        flow_gates = data.get("gates") or {}
        if isinstance(flow_gates, dict):
            gates.update(str(gate) for gate in flow_gates)
            behavioral = flow_gates.get("before_behavioral_implementation") or {}
            checks = behavioral.get("checks") if isinstance(behavioral, dict) else ()
            has_tdd = has_tdd or {"red_executed", "red_failed_for_expected_reason"}.issubset(checks or ())
        review = data.get("review") or {}
        has_strict_review = has_strict_review or (
            "strict_review" in stages
            or (isinstance(review, dict) and review.get("strict") is True)
        )
    return tuple(sorted(stages)), tuple(sorted(gates)), has_tdd, has_strict_review


def _limitations(*, has_tdd: bool, has_strict_review: bool) -> tuple[CapabilityLimitation, ...]:
    assessments = (
        assess_invariant(
            invariant_id="tdd-red-before-behavior",
            source_reference="FR-004",
            represented=has_tdd,
            technical_enforcement=False,
        ),
        assess_invariant(
            invariant_id="strict-review",
            source_reference="FR-004",
            represented=has_strict_review,
            technical_enforcement=False,
        ),
    )
    limitations = [
        limitation
        for assessment in assessments
        if (limitation := to_generic_limitation(assessment, capability="skills")) is not None
    ]
    return tuple(sorted(
        limitations,
        key=lambda item: (item.requirement_id, item.capability, item.source_reference),
    ))
