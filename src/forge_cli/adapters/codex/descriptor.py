from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import as_file, files
from pathlib import Path
from tempfile import NamedTemporaryFile

from forge_cli.adapters.manifest import AdapterManifest, load_adapter_manifest
from forge_cli.adapters.codex.evidence import CapabilityEvidence, load_packaged_codex_evidence


@dataclass(frozen=True)
class CodexAdapterDescriptor:
    manifest: AdapterManifest
    evidence: tuple[CapabilityEvidence, ...]


def parse_codex_adapter_manifest(content: str) -> AdapterManifest:
    with NamedTemporaryFile("w", encoding="utf-8", suffix=".yml", delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    try:
        return load_adapter_manifest(temporary)
    finally:
        temporary.unlink(missing_ok=True)


def load_packaged_codex_manifest() -> AdapterManifest:
    resource = files("forge_cli.adapters.codex").joinpath("resources", "adapter.yml")
    with as_file(resource) as path:
        return load_adapter_manifest(path)


def load_codex_adapter_descriptor() -> CodexAdapterDescriptor:
    return CodexAdapterDescriptor(
        manifest=load_packaged_codex_manifest(),
        evidence=load_packaged_codex_evidence(),
    )
