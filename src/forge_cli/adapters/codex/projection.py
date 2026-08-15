"""Deterministic, in-memory Codex projection resources."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files

import yaml


@dataclass(frozen=True)
class CodexProjectionInput:
    flow_id: str
    flow_content: str
    contract_content: str
    protocol_id: int = 1


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
    return resource.read_text(encoding="utf-8").rstrip()


def _resource(name: str, content: str) -> CodexProjectionResource:
    normalized = content.rstrip() + "\n"
    return CodexProjectionResource(name=name, content=normalized, digest=sha256(normalized.encode("utf-8")).hexdigest())


def _label(stage_id: str) -> str:
    known = {
        "specification_review": "Specification Review",
        "tdd_implementation": "TDD Implementation",
        "verification": "Verification",
        "strict_review": "Strict Review",
        "completion": "Completion",
    }
    return known.get(stage_id, stage_id.replace("_", " ").title())


def _instructions(protocol_id: int, flow_id: str, flow_content: str) -> str:
    data = yaml.safe_load(flow_content) or {}
    stages = data.get("stages") or []
    gates = data.get("gates") or {}
    stage_ids = [item.get("id") for item in stages if isinstance(item, dict) and item.get("id")]

    lines = [load_workflow_skill_template(), ""]
    if stage_ids:
        lines.extend(("### Required stage order", ""))
        lines.extend(f"{index}. {_label(stage_id)}" for index, stage_id in enumerate(stage_ids, 1))
        lines.append("")

    checks = set((gates.get("before_behavioral_implementation") or {}).get("checks") or [])
    if "red_executed" in checks:
        lines.append("- RED must be executed.")
    if "red_failed_for_expected_reason" in checks:
        lines.append("- RED must fail for the expected reason.")
    if {"red_executed", "red_failed_for_expected_reason"}.issubset(checks):
        lines.append("- Behavioral implementation requires valid RED.")
    if checks:
        lines.append("")

    required = set((gates.get("before_completion") or {}).get("require") or [])
    if "verification_passed" in required:
        lines.append("- Completion requires Verification to pass.")
    if "review_passed" in required:
        lines.append("- Completion requires Strict Review to pass.")
    if "blocking_review_threads_resolved" in required:
        lines.append(
            "- Completion requires all blocking review threads on any active "
            "external review surface to be resolved."
        )

    if protocol_id >= 2 and flow_id in {"fast", "standard", "full"}:
        lines.extend(
            (
                "",
                "### Reviewer/Resolver independence",
                "",
                "- Under Protocol 2, Strict Review must run in an Execution and Execution Context independent from the implementation or resolution that produced the revision under review.",
                "- Merely changing Role inside the same conversation, thread, session, or reasoning context is self-review and cannot satisfy Strict Review.",
                "- Record implementation/resolution and review executions in repository-native `provenance.yml`; a passed Review Iteration references them through `subject_provenance` and `reviewer_provenance`.",
                "- Both provenance records must bind to the same revision. Pairwise-distinct invented strings without matching provenance records are not evidence.",
                "- `claimed` identity is insufficient for `review_passed`; Core requires at least `recorded` provenance and treats `verified` provenance as the stronger observer-backed level.",
                "- Reviewer execution and context identifiers must both differ from the subject record. Distinct executions do not rescue a shared context, and distinct contexts do not rescue a shared execution.",
                "- After blocking findings are resolved, re-review must target the resolved revision and be independent from the Resolution provenance that produced it.",
            )
        )

    return "\n".join(lines).rstrip()


def generate_codex_projection_bundle(canonical: CodexProjectionInput) -> CodexProjectionBundle:
    flow_resource = _resource(
        "forge-flow.md",
        "\n".join((
            "# Forge Flow Projection",
            "",
            f"Flow: {canonical.flow_id}",
            "",
            "This resource is a derived Forge projection for Codex.",
            "Repository-native Forge state remains authoritative.",
            "",
            _instructions(canonical.protocol_id, canonical.flow_id, canonical.flow_content),
            "",
            "## Canonical Flow",
            "",
            canonical.flow_content,
        )),
    )
    contract_resource = _resource(
        "forge-contract.md",
        "\n".join((
            "# Forge Contract Projection",
            "",
            f"Flow context: {canonical.flow_id}",
            "",
            "This resource is a derived Forge projection for Codex.",
            "",
            "## Canonical Engineering Contract",
            "",
            canonical.contract_content,
        )),
    )
    resources = tuple(sorted((flow_resource, contract_resource), key=lambda item: item.name))
    return CodexProjectionBundle(adapter_id="codex", flow_id=canonical.flow_id, resources=resources)
