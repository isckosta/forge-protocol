"""Deterministic, in-memory resources for a repository-local Claude Code
skill, CLAUDE.md pointer, and illustrative enforcement hook."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
from typing import Iterable

import yaml


@dataclass(frozen=True)
class ClaudeCodeProjectionInput:
    """Compatibility input for callers projecting one effective Flow."""

    flow_id: str
    flow_content: str
    contract_content: str
    protocol_id: int = 1
    artifact_structure_content: str = ""
    interaction_language: str = ""


@dataclass(frozen=True)
class ClaudeCodeProjectionResource:
    name: str
    content: str
    digest: str


@dataclass(frozen=True)
class ClaudeCodeProjectionBundle:
    adapter_id: str
    flow_id: str
    resources: tuple[ClaudeCodeProjectionResource, ...]


_HOOK_RELATIVE_PATH = "skills/forge/hooks/check-manifest-edit.sh"


def load_workflow_skill_template() -> str:
    resource = files("forge_cli.adapters.claude_code").joinpath("resources", "skills", "workflow.md")
    return resource.read_text(encoding="utf-8").strip()


def _normalized(content: str) -> str:
    return content.rstrip() + "\n"


def _resource(name: str, content: str) -> ClaudeCodeProjectionResource:
    normalized = _normalized(content)
    return ClaudeCodeProjectionResource(
        name=name,
        content=normalized,
        digest=sha256(normalized.encode("utf-8")).hexdigest(),
    )


def _interaction_language_line(interaction_language: str) -> str:
    effective = interaction_language or "auto"
    if effective == "auto":
        return (
            "Interaction language: auto -- use the active chat's observed "
            "language if there is one, otherwise English (C-070-C-073)."
        )
    return (
        f"Interaction language: {effective} (project configuration takes "
        "precedence -- C-072)."
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


def _hook_frontmatter_lines() -> tuple[str, ...]:
    return (
        "hooks:",
        "  PreToolUse:",
        '    - matcher: "Bash"',
        "      hooks:",
        "        - type: command",
        f'          command: "${{CLAUDE_PROJECT_DIR}}/.claude/{_HOOK_RELATIVE_PATH}"',
    )


def _skill_content(
    flows: Iterable[tuple[str, str]],
    protocol_id: int,
    *,
    has_artifact_structure: bool,
    interaction_language: str = "",
) -> str:
    effective_flows = tuple(flows)
    gate_instructions = _gate_instructions(effective_flows, protocol_id)
    return "\n".join((
        "---",
        "name: forge",
        "description: Use for Forge-governed engineering Changes in this repository.",
        *_hook_frontmatter_lines(),
        "---",
        "",
        load_workflow_skill_template(),
        "",
        _reference_links(effective_flows, has_artifact_structure=has_artifact_structure),
        "",
        _interaction_language_line(interaction_language),
        "",
        "## Illustrative enforcement hook",
        "",
        "This skill registers a `PreToolUse` hook (active once this skill has "
        "been invoked in a session, not from session start) that denies a "
        "`Bash` command matching an in-place-mutation shape "
        "(`sed -i`/`perl -i`/`truncate`/output redirection) targeting "
        "`.forge/changes/*/manifest.yml`, `provenance.yml`, or `review.md`. "
        "It does not match read-only or version-control commands "
        "(`cat`/`ls`/`git add`/`git commit`/`git status`/`git diff`/`git "
        "show`/`grep`) against the same paths. This is Core's honest "
        "boundary (C-073): the hook enforces this one narrow, "
        "mechanically-checkable pattern; it is not a general security "
        "boundary and is not represented as one.",
        "",
        gate_instructions,
    ))


def _claude_md_pointer(interaction_language: str = "") -> str:
    return "\n".join((
        "<!-- forge:begin -->",
        "## Forge",
        "",
        "This repository is Forge-governed. See the `forge` skill "
        "(`.claude/skills/forge/SKILL.md`) for the full Engineering "
        "Contract, effective Flows, and workflow instructions -- this "
        "pointer intentionally does not restate them.",
        "",
        _interaction_language_line(interaction_language),
        "<!-- forge:end -->",
    ))


def _hook_script_content() -> str:
    return "\n".join((
        "#!/bin/sh",
        "set -eu",
        "",
        "# Forge CHG-0018 FR-006: illustrative PreToolUse enforcement hook.",
        "# Denies in-place shell mutation of Forge review-control metadata;",
        "# never matches read-only or version-control commands (see SKILL.md).",
        "input=\"$(cat)\"",
        "command=\"$(printf '%s' \"$input\" | jq -r '.tool_input.command // empty')\"",
        "",
        "case \"$command\" in",
        "  *.forge/changes/*manifest.yml*|*.forge/changes/*provenance.yml*|*.forge/changes/*review.md*)",
        "    case \"$command\" in",
        "      *'sed -i'*|*'perl -i'*|*truncate*|*'>'*)",
        "        printf '%s\\n' '{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"Forge review-control metadata (manifest.yml/provenance.yml/review.md) must not be mutated via shell redirection or in-place editing; use the normal Write/Edit tool path so changes stay auditable (CHG-0018 FR-006).\"}}'",
        "        exit 0",
        "        ;;",
        "    esac",
        "    ;;",
        "esac",
        "exit 0",
    ))


def generate_claude_code_skill_bundle(
    *,
    contract_content: str,
    flows: Iterable[tuple[str, str]],
    protocol_id: int = 1,
    artifact_structure_content: str = "",
    interaction_language: str = "",
) -> ClaudeCodeProjectionBundle:
    """Render the already-resolved effective Forge inputs for Claude Code."""
    effective_flows = tuple(flows)
    flow_resources: list[ClaudeCodeProjectionResource] = []
    seen_flow_ids: set[str] = set()
    for flow_id, flow_content in effective_flows:
        if flow_id in seen_flow_ids:
            raise ValueError(f"Duplicate effective Claude Code Flow: {flow_id}")
        seen_flow_ids.add(flow_id)
        flow_resources.append(
            _resource(f"skills/forge/references/flows/{flow_id}.yml", flow_content)
        )

    has_artifact_structure = bool(artifact_structure_content)
    resources = (
        _resource(
            "skills/forge/SKILL.md",
            _skill_content(
                effective_flows,
                protocol_id,
                has_artifact_structure=has_artifact_structure,
                interaction_language=interaction_language,
            ),
        ),
        _resource("skills/forge/references/engineering-contract.md", contract_content),
        *(
            (_resource("skills/forge/references/artifact-structure.md", artifact_structure_content),)
            if has_artifact_structure
            else ()
        ),
        _resource(_HOOK_RELATIVE_PATH, _hook_script_content()),
        _resource("CLAUDE.md", _claude_md_pointer(interaction_language)),
        *flow_resources,
    )
    return ClaudeCodeProjectionBundle(
        adapter_id="claude-code",
        flow_id=next(iter(sorted(seen_flow_ids)), ""),
        resources=tuple(sorted(resources, key=lambda item: item.name)),
    )


def generate_claude_code_projection_bundle(
    canonical: ClaudeCodeProjectionInput,
) -> ClaudeCodeProjectionBundle:
    """Project one Flow through the same repository-skill renderer."""
    return generate_claude_code_skill_bundle(
        contract_content=canonical.contract_content,
        flows=((canonical.flow_id, canonical.flow_content),),
        protocol_id=canonical.protocol_id,
        artifact_structure_content=canonical.artifact_structure_content,
        interaction_language=canonical.interaction_language,
    )
