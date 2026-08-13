from pathlib import Path


class ProtocolResourcesUnavailableError(RuntimeError):
    """Raised when canonical Forge Protocol resources cannot be located."""


def resolve_protocol_root(
    package_root: Path | None = None,
    source_protocol: Path | None = None,
) -> Path:
    """Resolve packaged Protocol resources, with source-tree fallback for development."""
    package_root = package_root or Path(__file__).resolve().parent
    packaged_protocol = package_root / "resources" / "protocol"
    if packaged_protocol.is_dir():
        return packaged_protocol

    source_protocol = source_protocol or Path(__file__).resolve().parents[2] / "protocol"
    if source_protocol.is_dir():
        return source_protocol

    raise ProtocolResourcesUnavailableError(
        "Canonical Forge Protocol resources are unavailable."
    )
