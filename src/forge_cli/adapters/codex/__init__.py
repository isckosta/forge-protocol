"""Codex Harness Adapter descriptor and capability evidence."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from forge_cli.adapters.manifest import AdapterManifest


@dataclass(frozen=True)
class CapabilityEvidence:
    capability: str
    status: str
    source: str
    observed_on: str


@dataclass(frozen=True)
class CodexAdapterDescriptor:
    manifest: AdapterManifest
    evidence: tuple[CapabilityEvidence, ...]


_OBSERVED_ON = "2026-08-13"
_CODEX_USE_CASES = "https://developers.openai.com/codex/use-cases"
_FORGE_GENERATED_FILES = "forge://CHG-0004/generated-files"


def load_codex_adapter_descriptor() -> CodexAdapterDescriptor:
    capabilities = MappingProxyType(
        {
            "persistent_instructions": False,
            "commands": False,
            "skills": True,
            "hooks": False,
            "agent_roles": False,
            "generated_files": True,
        }
    )

    manifest = AdapterManifest(
        adapter_id="codex",
        version="0.1.0",
        harness="codex",
        protocol_min=1,
        protocol_max_exclusive=2,
        capabilities=capabilities,
    )

    evidence = tuple(
        sorted(
            (
                CapabilityEvidence("agent_roles", "unsupported", _CODEX_USE_CASES, _OBSERVED_ON),
                CapabilityEvidence("commands", "unsupported", _CODEX_USE_CASES, _OBSERVED_ON),
                CapabilityEvidence("generated_files", "supported", _FORGE_GENERATED_FILES, _OBSERVED_ON),
                CapabilityEvidence("hooks", "unsupported", _CODEX_USE_CASES, _OBSERVED_ON),
                CapabilityEvidence("persistent_instructions", "unsupported", _CODEX_USE_CASES, _OBSERVED_ON),
                CapabilityEvidence("skills", "supported", _CODEX_USE_CASES, _OBSERVED_ON),
            ),
            key=lambda item: item.capability,
        )
    )

    return CodexAdapterDescriptor(manifest=manifest, evidence=evidence)
