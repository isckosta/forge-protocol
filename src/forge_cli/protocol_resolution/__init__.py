"""Forge Protocol resolution boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ProtocolResolutionError(RuntimeError):
    """Base error for deterministic Protocol resolution failures."""


class UnknownCanonicalFlowError(ProtocolResolutionError):
    """Raised when a project references a canonical Flow that does not exist."""


class InvalidProjectFlowConfigurationError(ProtocolResolutionError):
    """Raised when project Flow configuration attempts unsupported redefinition."""


class CanonicalContractUnavailableError(ProtocolResolutionError):
    """Raised when the canonical Engineering Contract cannot be resolved."""


_ALLOWED_PROJECT_FLOW_KEYS = {"schema", "flow", "review", "testing"}


@dataclass(frozen=True)
class EffectiveContract:
    """Ordered canonical Contract plus an optional additive project extension."""

    canonical: str
    project_extension: str = ""

    @property
    def text(self) -> str:
        if not self.project_extension:
            return self.canonical
        return f"{self.canonical.rstrip()}\n\n{self.project_extension.lstrip()}"


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise InvalidProjectFlowConfigurationError(
            f"Expected a YAML mapping in {path}."
        )
    return data


def _versioned_protocol_root(protocol_root: Path, protocol_id: int) -> Path:
    """Resolve immutable version-specific resources without relabeling Protocol 1."""
    if protocol_id == 1:
        return protocol_root
    candidate = protocol_root / "versions" / str(protocol_id)
    return candidate if candidate.is_dir() else protocol_root


def resolve_effective_flow(
    protocol_root: Path,
    project_root: Path,
    flow_id: str,
    protocol_id: int = 1,
) -> dict[str, dict[str, Any]]:
    """Resolve canonical and project Flow layers without destructive merging."""

    project_flow_path = project_root / ".forge" / "flows" / f"{flow_id}.yml"
    project = _load_yaml(project_flow_path)

    unsupported = set(project) - _ALLOWED_PROJECT_FLOW_KEYS
    if unsupported:
        names = ", ".join(sorted(unsupported))
        raise InvalidProjectFlowConfigurationError(
            f"Project Flow cannot redefine canonical sections: {names}."
        )

    if project.get("schema") != "forge/project-flow@1":
        raise InvalidProjectFlowConfigurationError(
            f"Unsupported project Flow schema in {project_flow_path}."
        )

    flow = project.get("flow")
    if not isinstance(flow, dict) or not isinstance(flow.get("canonical"), str):
        raise InvalidProjectFlowConfigurationError(
            f"Project Flow must reference a canonical Flow in {project_flow_path}."
        )

    canonical_id = flow["canonical"]
    versioned_root = _versioned_protocol_root(protocol_root, protocol_id)
    canonical_path = versioned_root / "flows" / f"{canonical_id}.yml"
    if not canonical_path.is_file():
        canonical_path = protocol_root / "flows" / f"{canonical_id}.yml"
    if not canonical_path.is_file():
        raise UnknownCanonicalFlowError(
            f"Unknown canonical Forge Flow: {canonical_id}."
        )

    canonical = _load_yaml(canonical_path)
    canonical_flow = canonical.get("flow")
    if not isinstance(canonical_flow, dict) or canonical_flow.get("id") != canonical_id:
        raise UnknownCanonicalFlowError(
            f"Canonical Flow {canonical_id} is not internally consistent."
        )

    return {"canonical": canonical, "project": project}


def resolve_effective_contract(
    protocol_root: Path,
    project_root: Path,
    protocol_id: int = 1,
) -> EffectiveContract:
    """Compose the selected immutable canonical Contract with a project extension."""

    versioned_root = _versioned_protocol_root(protocol_root, protocol_id)
    canonical_path = versioned_root / "contract" / "engineering.md"
    if not canonical_path.is_file():
        raise CanonicalContractUnavailableError(
            f"Canonical Protocol {protocol_id} Engineering Contract is unavailable at {canonical_path}."
        )

    canonical = canonical_path.read_text(encoding="utf-8")
    project_path = project_root / ".forge" / "contract" / "engineering.md"
    project_extension = (
        project_path.read_text(encoding="utf-8") if project_path.is_file() else ""
    )

    return EffectiveContract(
        canonical=canonical,
        project_extension=project_extension,
    )
