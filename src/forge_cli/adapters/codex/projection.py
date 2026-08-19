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
    protocol_id: int = 1
    artifact_structure_content: str = ""


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


_REVIEWER_RESOLVER_INDEPENDENCE_LINES: tuple[str, ...] = (
    "",
    "### Reviewer/Resolver independence",
    "",
    "- Under Protocol 2, Strict Review must run in an Execution and Execution Context "
    "independent from the implementation or resolution that produced the revision under review.",
    "- Merely changing Role inside the same conversation, thread, session, or reasoning "
    "context is self-review and cannot satisfy Strict Review.",
    "- Finish the Implementation/Resolution and all reviewable evidence before freezing the "
    "review subject.",
    "- Before freezing, ensure the effective reviewable Git workspace is clean: no committed "
    "post-subject delta, staged reviewable changes, unstaged reviewable changes, or "
    "Git-visible untracked reviewable files.",
    "- Identify the concrete immutable subject revision. In Git, use the subject commit SHA; "
    "`revision.id` alone is not sufficient.",
    "- Record the frozen subject in `provenance.yml`; the Review Iteration references it "
    "through `subject_provenance`.",
    "- Only the exact Change-local `manifest.yml`, `provenance.yml`, and `review.md` paths are "
    "review-control metadata that may differ after the freeze; do not generalize that "
    "exception to the Change directory, matching basenames, symlinks, or rename targets.",
    "- Git-ignored cache/editor/temp files do not count as reviewable workspace mutations for "
    "the freeze invariant.",
    "- Re-check committed, staged, unstaged, and untracked reviewable deltas after recording "
    "review-control metadata.",
    "- Start Strict Review against the frozen subject, not an ambiguous later HEAD or dirty "
    "checkout.",
    "- Record the independent Reviewer execution through `reviewer_provenance`; it must bind "
    "to the exact same logical revision and immutable reference.",
    "- Reviewer Execution and Context must both differ from the subject. Distinct invented IDs "
    "are not evidence.",
    "- `claimed` is insufficient; `recorded` is repository-native self-recorded evidence and "
    "`verified` is stronger observer-backed evidence.",
    "- After blocking findings are resolved, freeze the new Resolution revision and re-review "
    "that concrete revision independently.",
)


def _gate_instructions(flows: Iterable[tuple[str, str]], protocol_id: int) -> str:
    sections: list[str] = []
    for flow_id, content in sorted(flows, key=lambda item: item[0]):
        data = yaml.safe_load(content) or {}
        gates = data.get("gates") or {}
        if not isinstance(gates, dict):
            continue
        behavioral = gates.get("before_behavioral_implementation") or {}
        checks = behavioral.get("checks") if isinstance(behavioral, dict) else ()
        checks = set(checks or ())
        completion = gates.get("before_completion") or {}
        required = completion.get("require") if isinstance(completion, dict) else ()
        required = set(required or ())

        pre_implementation = gates.get("before_implementation") or {}
        pre_implementation_required = (
            pre_implementation.get("require") if isinstance(pre_implementation, dict) else ()
        ) or ()

        lines: list[str] = []
        if pre_implementation_required:
            lines.append(
                "- Implementation MUST NOT begin until: "
                f"{', '.join(pre_implementation_required)}."
            )
        if "red_executed" in checks:
            lines.append("- RED must be executed.")
        if "red_failed_for_expected_reason" in checks:
            lines.append("- RED must fail for the expected reason.")
        if "verification_passed" in required:
            lines.append("- Completion requires Verification to pass.")
        if "review_passed" in required:
            lines.append("- Completion requires Strict Review to pass.")
        if "blocking_review_threads_resolved" in required:
            lines.append(
                "- Completion requires all blocking review threads on any active "
                "external review surface to be resolved."
            )
        if "documentation_impact_evaluated" in required:
            lines.append("- Completion requires Documentation Impact to be evaluated.")
        if "required_documentation_updated" in required:
            lines.append("- Completion requires required documentation to be updated.")
        if "tdd_compliant_or_explicitly_excepted" in required:
            lines.append(
                "- Completion requires TDD compliance or an explicit, recorded exception."
            )
        if protocol_id >= 2 and flow_id in {"fast", "standard", "full"}:
            lines.extend(_REVIEWER_RESOLVER_INDEPENDENCE_LINES)
        if lines:
            sections.append("\n".join((f"### Flow `{flow_id}` gate obligations", "", *lines)))
    return "\n\n".join(sections)


def _reference_links(flows: Iterable[tuple[str, str]], *, has_artifact_structure: bool) -> str:
    flow_ids = tuple(sorted(flow_id for flow_id, _ in flows))
    return "\n".join((
        "## Effective Forge references",
        "",
        "- [Engineering Contract](references/engineering-contract.md)",
        *(("- [Artifact Structure](references/artifact-structure.md)",) if has_artifact_structure else ()),
        *(f"- [Flow `{flow_id}`](references/flows/{flow_id}.yml)" for flow_id in flow_ids),
    ))


def _skill_content(
    flows: Iterable[tuple[str, str]],
    protocol_id: int,
    *,
    has_artifact_structure: bool,
) -> str:
    effective_flows = tuple(flows)
    gate_instructions = _gate_instructions(effective_flows, protocol_id)
    return "\n".join((
        "---",
        "name: forge",
        "description: Use for Forge-governed engineering Changes in this repository.",
        "---",
        "",
        load_workflow_skill_template(),
        "",
        _reference_links(effective_flows, has_artifact_structure=has_artifact_structure),
        "",
        gate_instructions,
    ))


def generate_codex_skill_bundle(
    *,
    contract_content: str,
    flows: Iterable[tuple[str, str]],
    protocol_id: int = 1,
    artifact_structure_content: str = "",
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

    has_artifact_structure = bool(artifact_structure_content)
    resources = (
        _resource(
            "SKILL.md",
            _skill_content(effective_flows, protocol_id, has_artifact_structure=has_artifact_structure),
        ),
        _resource("references/engineering-contract.md", contract_content),
        *((_resource("references/artifact-structure.md", artifact_structure_content),) if has_artifact_structure else ()),
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
        protocol_id=canonical.protocol_id,
        artifact_structure_content=canonical.artifact_structure_content,
    )
