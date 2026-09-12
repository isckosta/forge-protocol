from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import as_file, files
from pathlib import Path
from tempfile import NamedTemporaryFile

from forge_cli.adapters.github_copilot.evidence import (
    CapabilityEvidence,
    load_packaged_github_copilot_evidence,
)
from forge_cli.adapters.manifest import AdapterManifest, load_adapter_manifest


@dataclass(frozen=True)
class GitHubCopilotAdapterDescriptor:
    manifest: AdapterManifest
    evidence: tuple[CapabilityEvidence, ...]


def parse_github_copilot_adapter_manifest(content: str) -> AdapterManifest:
    with NamedTemporaryFile("w", encoding="utf-8", suffix=".yml", delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    try:
        return load_adapter_manifest(temporary)
    finally:
        temporary.unlink(missing_ok=True)


def load_packaged_github_copilot_manifest() -> AdapterManifest:
    resource = files("forge_cli.adapters.github_copilot").joinpath("resources", "adapter.yml")
    with as_file(resource) as path:
        return load_adapter_manifest(path)


def load_github_copilot_adapter_descriptor() -> GitHubCopilotAdapterDescriptor:
    return GitHubCopilotAdapterDescriptor(
        manifest=load_packaged_github_copilot_manifest(),
        evidence=load_packaged_github_copilot_evidence(),
    )
