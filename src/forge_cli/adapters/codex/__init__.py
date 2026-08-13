from __future__ import annotations

from dataclasses import dataclass

from forge_cli.adapters.manifest import AdapterManifest
from forge_cli.adapters.codex.descriptor import load_packaged_codex_manifest
from forge_cli.adapters.codex.evidence import CapabilityEvidence, load_packaged_codex_evidence


@dataclass(frozen=True)
class CodexAdapterDescriptor:
    manifest: AdapterManifest
    evidence: tuple[CapabilityEvidence, ...]


def load_codex_adapter_descriptor() -> CodexAdapterDescriptor:
    return CodexAdapterDescriptor(
        manifest=load_packaged_codex_manifest(),
        evidence=load_packaged_codex_evidence(),
    )
