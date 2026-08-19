"""Harness-agnostic invariant support classification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from forge_cli.adapters.capabilities import CapabilityLimitation


class InvariantSupport(StrEnum):
    ENFORCED = "enforced"
    REPRESENTED = "represented"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class InvariantAssessment:
    invariant_id: str
    source_reference: str
    support: InvariantSupport


def assess_invariant(*, invariant_id: str, source_reference: str, represented: bool, technical_enforcement: bool) -> InvariantAssessment:
    if not represented:
        support = InvariantSupport.UNSUPPORTED
    elif technical_enforcement:
        support = InvariantSupport.ENFORCED
    else:
        support = InvariantSupport.REPRESENTED
    return InvariantAssessment(invariant_id, source_reference, support)


def to_generic_limitation(assessment: InvariantAssessment, *, capability: str) -> CapabilityLimitation | None:
    if assessment.support is InvariantSupport.ENFORCED:
        return None
    return CapabilityLimitation(assessment.invariant_id, capability, assessment.source_reference)
