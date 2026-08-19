"""Generic Harness Driver contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from forge_cli.adapters.capabilities import CapabilityLimitation
from forge_cli.adapters.manifest import AdapterManifest
from forge_cli.adapters.planner import ProjectedArtifact
from forge_cli.adapters.validation import AdapterRepresentation


@dataclass(frozen=True)
class AdapterProjectionContext:
    project_protocol: int
    flows: tuple[tuple[str, str], ...]
    contract_content: str
    target: str
    artifact_structure_content: str = ""
    interaction_language: str = ""


@dataclass(frozen=True)
class AdapterProjection:
    artifacts: tuple[ProjectedArtifact, ...]
    limitations: tuple[CapabilityLimitation, ...]
    representation: AdapterRepresentation


class HarnessDriver(Protocol):
    @property
    def manifest(self) -> AdapterManifest:
        raise NotImplementedError

    @property
    def default_target(self) -> str | None:
        raise NotImplementedError

    def validate_publication_root(self, publication_root: str) -> None: ...

    def project(self, context: AdapterProjectionContext) -> AdapterProjection: ...
