"""Resolution of packaged Forge Capability definitions."""

from __future__ import annotations

from pathlib import Path


class CapabilityResourcesUnavailableError(RuntimeError):
    """Raised when canonical Capability resources cannot be located."""


def resolve_capability_root(
    package_root: Path | None = None,
    source_capabilities: Path | None = None,
) -> Path:
    """Resolve packaged definitions, with a source-tree development fallback."""
    package_root = package_root or Path(__file__).resolve().parent
    packaged = package_root / "resources" / "capabilities"
    if packaged.is_dir():
        return packaged

    source_capabilities = source_capabilities or Path(__file__).resolve().parents[2] / "capabilities"
    if source_capabilities.is_dir():
        return source_capabilities

    raise CapabilityResourcesUnavailableError(
        "Canonical Forge Capability resources are unavailable."
    )
