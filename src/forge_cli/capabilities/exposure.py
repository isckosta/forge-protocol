"""Harness-independent exposure metadata derived from canonical capabilities."""

from __future__ import annotations

from dataclasses import dataclass
import re

from forge_cli.capabilities.model import Capability


_INVOCATION_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_RESERVED_INVOCATION_IDS = frozenset({"forge", "references"})


@dataclass(frozen=True)
class CapabilityExposure:
    """Stable identity mapped by each Harness to its supported surface."""

    capability: Capability
    invocation_id: str


def derive_capability_exposures(
    capabilities: tuple[Capability, ...],
) -> tuple[CapabilityExposure, ...]:
    """Derive deterministic exposure identities without defining a Harness UI."""
    exposures: list[CapabilityExposure] = []
    seen: set[str] = set()
    for capability in sorted(capabilities, key=lambda item: item.id):
        if not _INVOCATION_ID.fullmatch(capability.id):
            raise ValueError(f"Invalid capability invocation id: {capability.id!r}")
        if capability.id in _RESERVED_INVOCATION_IDS:
            raise ValueError(f"Reserved capability invocation id: {capability.id}")
        if capability.id in seen:
            raise ValueError(f"Duplicate capability invocation id: {capability.id}")
        seen.add(capability.id)
        exposures.append(CapabilityExposure(capability, capability.id))
    return tuple(exposures)
