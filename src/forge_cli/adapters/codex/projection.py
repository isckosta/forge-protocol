"""Deterministic, in-memory resources for a repository-local Codex skill."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
from typing import Iterable


@dataclass(frozen=True)
class CodexProjectionInput:
    """Compatibility input for callers projecting one effective Flow."""

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


def load_workflow_skill_template() -> str:
    resource = files("forge_cli.adapters.codex").joinpath("resources", "skills", "workflow.md")
    return resource.read_text(encoding="utf-8").strip()


def _normalized(content: str) -> str:
    return content.rstrip() + "\n"


def _resource(name: str, content: str) -> CodexProjectionResource:
    normalized = _normalized(content)
    return CodexProjectionResource(
        name=name,
        content=normalized,
        digest=sha256(normalized.encode("utf-8")).hexdigest(),
    )


def _skill_content() -> str:
    return "\n".join((
        "---",
        "name: forge",
        "description: Use for Forge-governed engineering Changes in this repository.",
        "---",
        "",
        load_workflow_skill_template(),
    ))


def generate_codex_skill_bundle(
    *,
    contract_content: str,
    flows: Iterable[tuple[str, str]],
) -> CodexProjectionBundle:
    """Render only the already-resolved effective Forge inputs for Codex."""
    flow_resources: list[CodexProjectionResource] = []
    seen_flow_ids: set[str] = set()
    for flow_id, flow_content in flows:
        if flow_id in seen_flow_ids:
            raise ValueError(f"Duplicate effective Codex Flow: {flow_id}")
        seen_flow_ids.add(flow_id)
        flow_resources.append(_resource(f"references/flows/{flow_id}.yml", flow_content))

    resources = (
        _resource("SKILL.md", _skill_content()),
        _resource("references/engineering-contract.md", contract_content),
        *flow_resources,
    )
    return CodexProjectionBundle(
        adapter_id="codex",
        flow_id=next(iter(sorted(seen_flow_ids)), ""),
        resources=tuple(sorted(resources, key=lambda item: item.name)),
    )


def generate_codex_projection_bundle(canonical: CodexProjectionInput) -> CodexProjectionBundle:
    """Project one Flow through the same repository-skill renderer."""
    return generate_codex_skill_bundle(
        contract_content=canonical.contract_content,
        flows=((canonical.flow_id, canonical.flow_content),),
    )
