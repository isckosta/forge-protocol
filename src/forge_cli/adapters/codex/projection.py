"""Deterministic, in-memory resources for a repository-local Codex skill."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
from typing import Iterable

import yaml

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


def _gate_instructions(flows: Iterable[tuple[str, str]]) -> str:
    red_executed = False
    red_failed_for_expected_reason = False
    verification_passed = False
    review_passed = False
    blocking_review_threads_resolved = False
    for _, content in flows:
        data = yaml.safe_load(content) or {}
        gates = data.get("gates") or {}
        if not isinstance(gates, dict):
            continue
        behavioral = gates.get("before_behavioral_implementation") or {}
        checks = behavioral.get("checks") if isinstance(behavioral, dict) else ()
        checks = set(checks or ())
        red_executed = red_executed or "red_executed" in checks
        red_failed_for_expected_reason = (
            red_failed_for_expected_reason or "red_failed_for_expected_reason" in checks
        )
        completion = gates.get("before_completion") or {}
        required = completion.get("require") if isinstance(completion, dict) else ()
        required = set(required or ())
        verification_passed = verification_passed or "verification_passed" in required
        review_passed = review_passed or "review_passed" in required
        blocking_review_threads_resolved = (
            blocking_review_threads_resolved or "blocking_review_threads_resolved" in required
        )

    lines: list[str] = []
    if red_executed:
        lines.append("- RED must be executed.")
    if red_failed_for_expected_reason:
        lines.append("- RED must fail for the expected reason.")
    if verification_passed:
        lines.append("- Completion requires Verification to pass.")
    if review_passed:
        lines.append("- Completion requires Strict Review to pass.")
    if blocking_review_threads_resolved:
        lines.append(
            "- Completion requires all blocking review threads on any active "
            "external review surface to be resolved."
        )
    return "\n".join(lines)


def _skill_content(flows: Iterable[tuple[str, str]]) -> str:
    gate_instructions = _gate_instructions(flows)
    return "\n".join((
        "---",
        "name: forge",
        "description: Use for Forge-governed engineering Changes in this repository.",
        "---",
        "",
        load_workflow_skill_template(),
        "",
        gate_instructions,
    ))


def generate_codex_skill_bundle(
    *,
    contract_content: str,
    flows: Iterable[tuple[str, str]],
) -> CodexProjectionBundle:
    """Render only the already-resolved effective Forge inputs for Codex."""
    effective_flows = tuple(flows)
    flow_resources: list[CodexProjectionResource] = []
    seen_flow_ids: set[str] = set()
    for flow_id, flow_content in effective_flows:
        if flow_id in seen_flow_ids:
            raise ValueError(f"Duplicate effective Codex Flow: {flow_id}")
        seen_flow_ids.add(flow_id)
        flow_resources.append(_resource(f"references/flows/{flow_id}.yml", flow_content))

    resources = (
        _resource("SKILL.md", _skill_content(effective_flows)),
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
