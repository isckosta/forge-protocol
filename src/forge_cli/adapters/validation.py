"""Harness-agnostic conformance validation for Forge Adapter representations."""

from __future__ import annotations

from dataclasses import dataclass

from forge_cli.adapters.capabilities import CapabilityLimitation


@dataclass(frozen=True)
class ConformanceRequirements:
    required_stages: tuple[str, ...]
    required_gates: tuple[str, ...]
    required_invariants: tuple[str, ...]
    tdd_red_required: bool
    strict_review_required: bool


@dataclass(frozen=True)
class AdapterRepresentation:
    stages: tuple[str, ...]
    gates: tuple[str, ...]
    represented_invariants: tuple[str, ...]
    enforced_invariants: tuple[str, ...]
    limitations: tuple[CapabilityLimitation, ...]
    repository_authority_preserved: bool
    red_before_behavior_preserved: bool = True
    strict_review_preserved: bool = True


@dataclass(frozen=True, order=True)
class ConformanceFinding:
    code: str
    subject: str = ""


def validate_conformance(
    requirements: ConformanceRequirements,
    representation: AdapterRepresentation,
) -> tuple[ConformanceFinding, ...]:
    """Validate that a Harness representation preserves already-resolved Forge semantics."""
    findings: list[ConformanceFinding] = []

    represented_stages = set(representation.stages)
    represented_gates = set(representation.gates)
    represented_invariants = set(representation.represented_invariants)
    enforced_invariants = set(representation.enforced_invariants)
    explicitly_limited = {
        limitation.requirement_id
        for limitation in representation.limitations
        if limitation.enforced is False
    }

    for stage in requirements.required_stages:
        if stage not in represented_stages:
            findings.append(
                ConformanceFinding(
                    code="E_FORGE_ADAPTER_STAGE_REMOVED",
                    subject=stage,
                )
            )

    for gate in requirements.required_gates:
        if gate not in represented_gates:
            findings.append(
                ConformanceFinding(
                    code="E_FORGE_ADAPTER_GATE_REMOVED",
                    subject=gate,
                )
            )

    for invariant in requirements.required_invariants:
        if invariant not in represented_invariants:
            findings.append(
                ConformanceFinding(
                    code="E_FORGE_ADAPTER_INVARIANT_REMOVED",
                    subject=invariant,
                )
            )
            continue

        if invariant not in enforced_invariants and invariant not in explicitly_limited:
            findings.append(
                ConformanceFinding(
                    code="E_FORGE_ADAPTER_ENFORCEMENT_UNDECLARED",
                    subject=invariant,
                )
            )

    if requirements.tdd_red_required and not representation.red_before_behavior_preserved:
        findings.append(
            ConformanceFinding(code="E_FORGE_ADAPTER_TDD_RED_BYPASSED")
        )

    if requirements.strict_review_required and not representation.strict_review_preserved:
        findings.append(
            ConformanceFinding(code="E_FORGE_ADAPTER_STRICT_REVIEW_BYPASSED")
        )

    if not representation.repository_authority_preserved:
        findings.append(
            ConformanceFinding(code="E_FORGE_ADAPTER_AUTHORITY_SHIFT")
        )

    return tuple(sorted(findings))
