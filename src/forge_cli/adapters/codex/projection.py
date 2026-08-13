"""Deterministic, in-memory Codex projection resources."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class CodexProjectionInput:
    flow_id: str
    flow_content: str
    contract_content: str


@dataclass(frozen=True)
class CodexProjectionResource:
    name: str
    content: str
    digest: str


@dataclass(frozen=True)
class CodexProjectionBundle:
    adapter_id: str
    flow_id: str
    resources: tuple[CodexProjectionResource, ...]


def _resource(name: str, content: str) -> CodexProjectionResource:
    normalized = content.rstrip() + "\n"
    return CodexProjectionResource(
        name=name,
        content=normalized,
        digest=sha256(normalized.encode("utf-8")).hexdigest(),
    )


def generate_codex_projection_bundle(
    canonical: CodexProjectionInput,
) -> CodexProjectionBundle:
    flow_resource = _resource(
        "forge-flow.md",
        "\n".join(
            (
                "# Forge Flow Projection",
                "",
                f"Flow: {canonical.flow_id}",
                "",
                "This resource is a derived Forge projection for Codex.",
                "Repository-native Forge state remains authoritative.",
                "",
                "## Canonical Flow",
                "",
                canonical.flow_content,
            )
        ),
    )
    contract_resource = _resource(
        "forge-contract.md",
        "\n".join(
            (
                "# Forge Contract Projection",
                "",
                f"Flow context: {canonical.flow_id}",
                "",
                "This resource is a derived Forge projection for Codex.",
                "",
                "## Canonical Engineering Contract",
                "",
                canonical.contract_content,
            )
        ),
    )

    resources = tuple(
        sorted(
            (flow_resource, contract_resource),
            key=lambda resource: resource.name,
        )
    )
    return CodexProjectionBundle(
        adapter_id="codex",
        flow_id=canonical.flow_id,
        resources=resources,
    )
