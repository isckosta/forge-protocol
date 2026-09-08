"""Forge Capability foundation: a minimal model and deterministic loader for a
canonical, Harness-independent capability definition (CAPABILITY.md).

See capabilities/README.md and capabilities/capability.md for the concept
and its minimal contract. This package introduces no registry, executor,
or lifecycle.
"""

from __future__ import annotations

from forge_cli.capabilities.exposure import CapabilityExposure, derive_capability_exposures
from forge_cli.capabilities.loader import (
    CapabilityDefinitionError,
    load_capability,
    load_capability_catalog,
)
from forge_cli.capabilities.model import Capability

__all__ = [
    "Capability",
    "CapabilityDefinitionError",
    "CapabilityExposure",
    "derive_capability_exposures",
    "load_capability",
    "load_capability_catalog",
]
