from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import as_file, files
from pathlib import Path
from tempfile import NamedTemporaryFile

from forge_cli.adapters.manifest import AdapterManifest, load_adapter_manifest
from forge_cli.adapters.claude_code.evidence import CapabilityEvidence, load_packaged_claude_code_evidence


@dataclass(frozen=True)
class ClaudeCodeAdapterDescriptor:
    manifest: AdapterManifest
    evidence: tuple[CapabilityEvidence, ...]


def parse_claude_code_adapter_manifest(content: str) -> AdapterManifest:
    with NamedTemporaryFile("w", encoding="utf-8", suffix=".yml", delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    try:
        return load_adapter_manifest(temporary)
    finally:
        temporary.unlink(missing_ok=True)


def load_packaged_claude_code_manifest() -> AdapterManifest:
    resource = files("forge_cli.adapters.claude_code").joinpath("resources", "adapter.yml")
    with as_file(resource) as path:
        return load_adapter_manifest(path)


def load_claude_code_adapter_descriptor() -> ClaudeCodeAdapterDescriptor:
    return ClaudeCodeAdapterDescriptor(
        manifest=load_packaged_claude_code_manifest(),
        evidence=load_packaged_claude_code_evidence(),
    )
