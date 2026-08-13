"""Harness capability requirements and explicit Forge limitations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Mapping


class RequirementSource(StrEnum):
    FORGE = "forge"
    ADAPTER_INTERNAL = "adapter_internal"


@dataclass(frozen=True)
class CapabilityRequirement:
    requirement_id: str
    capability: str
    source: RequirementSource
    source_reference: str


@dataclass(frozen=True)
class CapabilityLimitation:
    requirement_id: str
    capability: str
    source_reference: str
    enforced: bool = False


def evaluate_capability_requirements(
    *,
    declared_capabilities: Mapping[str, bool],
    requirements: Iterable[CapabilityRequirement],
) -> tuple[CapabilityLimitation, ...]:
    limitations: list[CapabilityLimitation] = []

    for requirement in requirements:
        if requirement.source is not RequirementSource.FORGE:
            continue
        if declared_capabilities.get(requirement.capability, False):
            continue

        limitations.append(
            CapabilityLimitation(
                requirement_id=requirement.requirement_id,
                capability=requirement.capability,
                source_reference=requirement.source_reference,
            )
        )

    return tuple(limitations)
