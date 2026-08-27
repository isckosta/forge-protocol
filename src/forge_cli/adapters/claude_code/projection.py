"""Deterministic, in-memory resources for a repository-local Claude Code
skill, CLAUDE.md pointer, and illustrative enforcement hook."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
from typing import Iterable

import yaml

from forge_cli.adapters.review_independence import (
    REVIEW_PROFILE_INSTRUCTION,
    REVIEWER_RESOLVER_INDEPENDENCE_LINES,
    REVIEWER_RESOLVER_INDEPENDENCE_POINTER,
    render_reviewer_resolver_independence_section,
)


@dataclass(frozen=True)
class ClaudeCodeProjectionInput:
    """Compatibility input for callers projecting one effective Flow."""

    flow_id: str
    flow_content: str
    contract_content: str
    protocol_id: int = 1
    artifact_structure_content: str = ""
    decision_rules_content: str = ""
    interaction_language: str = ""


@dataclass(frozen=True)
class ClaudeCodeProjectionResource:
    name: str
    content: str
    digest: str
    executable: bool = False


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


def _resource(
    name: str, content: str, *, executable: bool = False
) -> ClaudeCodeProjectionResource:
    normalized = _normalized(content)
    return ClaudeCodeProjectionResource(
        name=name,
        content=normalized,
        digest=sha256(normalized.encode("utf-8")).hexdigest(),
        executable=executable,
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


def _gate_instructions(flows: Iterable[tuple[str, str]], protocol_id: int) -> str:
    sections: list[str] = []
    independence_applies = False
    for flow_id, content in sorted(flows, key=lambda item: item[0]):
        data = yaml.safe_load(content) or {}
        review = data.get("review") or {}
        review_profile = review.get("profile", "strict") if isinstance(review, dict) else "strict"
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
            if protocol_id >= 2:
                lines.append(REVIEW_PROFILE_INSTRUCTION.get(review_profile, REVIEW_PROFILE_INSTRUCTION["strict"]))
            else:
                lines.append(REVIEW_PROFILE_INSTRUCTION["strict"])
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
            independence_applies = True
            lines.append(REVIEWER_RESOLVER_INDEPENDENCE_POINTER)
        if lines:
            sections.append("\n".join((f"### Flow `{flow_id}` gate obligations", "", *lines)))
    if independence_applies:
        sections.append(render_reviewer_resolver_independence_section().lstrip("\n"))
    return "\n\n".join(sections)


def _reference_links(
    flows: Iterable[tuple[str, str]],
    *,
    has_artifact_structure: bool,
    has_decision_rules: bool,
) -> str:
    flow_ids = tuple(sorted(flow_id for flow_id, _ in flows))
    return "\n".join((
        "## Effective Forge references",
        "",
        "- [Engineering Contract](references/engineering-contract.md)",
        *(("- [Artifact Structure](references/artifact-structure.md)",) if has_artifact_structure else ()),
        *(("- [Decision Rules](references/decision-rules.md)",) if has_decision_rules else ()),
        *(f"- [Flow `{flow_id}`](references/flows/{flow_id}.yml)" for flow_id in flow_ids),
    ))


def _hook_frontmatter_lines() -> tuple[str, ...]:
    lines: list[str] = ["hooks:", "  PreToolUse:"]
    for matcher in ("Bash", "Edit", "Write"):
        lines.extend((
            f'    - matcher: "{matcher}"',
            "      hooks:",
            "        - type: command",
            f'          command: "${{CLAUDE_PROJECT_DIR}}/.claude/{_HOOK_RELATIVE_PATH}"',
        ))
    return tuple(lines)


def _skill_content(
    flows: Iterable[tuple[str, str]],
    protocol_id: int,
    *,
    has_artifact_structure: bool,
    has_decision_rules: bool = False,
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
        _reference_links(
            effective_flows,
            has_artifact_structure=has_artifact_structure,
            has_decision_rules=has_decision_rules,
        ),
        "",
        _interaction_language_line(interaction_language),
        "",
        "## Illustrative enforcement hook",
        "",
        "This skill registers a `PreToolUse` hook (active once this skill has "
        "been invoked in a session, not from session start) that denies: a "
        "`Bash` command matching an in-place-mutation shape "
        "(`sed -i`/`perl -i`/`truncate`/output redirection); and a direct "
        "`Edit` or `Write` call whose target file is one of "
        "`.forge/changes/*/manifest.yml`, `provenance.yml`, or `review.md` "
        "(CHG-0045). It does not match read-only or version-control "
        "commands (`cat`/`ls`/`git add`/`git commit`/`git status`/`git "
        "diff`/`git show`/`grep`) against the same paths. This remains a "
        "partial, illustrative guard, not a general security boundary "
        "(C-073): it does not see MCP filesystem tools, `NotebookEdit`, "
        "or a mutation of these paths issued by a subagent's own tool "
        "calls -- whether Claude Code applies this session's `PreToolUse` "
        "hooks to subagent-issued calls is unverified by this Adapter, and "
        "is not claimed here.",
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
        "# Forge CHG-0018 FR-006 / CHG-0045 FR-006: illustrative PreToolUse",
        "# enforcement hook. Denies mutation of Forge review-control metadata",
        "# via Bash shell redirection/in-place editing, or via a direct",
        "# Edit/Write tool call targeting the same three paths; never matches",
        "# read-only or version-control commands (see SKILL.md). This remains",
        "# a partial, illustrative guard, not a general security boundary:",
        "# it does not see MCP filesystem tools, NotebookEdit, or (unverified)",
        "# subagent-issued tool calls.",
        "#",
        "# Strict Review R001 (CHG-0018 Iteration 1): a naive whole-string",
        "# substring match denied a plain git add/commit whenever an unrelated",
        "# '>' happened to appear anywhere else in the same command line (e.g.",
        "# inside a commit message, or an unrelated redirect earlier in a",
        "# compound command). Fixed by requiring the mutation token and the",
        "# protected path to be close together (bounded proximity, no shell",
        "# separator such as && / || / ; / | between them), via a single grep -E",
        "# check, instead of two independent whole-string case patterns.",
        "input=\"$(cat)\"",
        "tool_name=\"$(printf '%s' \"$input\" | jq -r '.tool_name // empty')\"",
        "",
        "if [ \"$tool_name\" = \"Edit\" ] || [ \"$tool_name\" = \"Write\" ]; then",
        "  file_path=\"$(printf '%s' \"$input\" | jq -r '.tool_input.file_path // empty')\"",
        "  case \"$file_path\" in",
        "    .forge/changes/*/manifest.yml|.forge/changes/*/provenance.yml|.forge/changes/*/review.md|*/.forge/changes/*/manifest.yml|*/.forge/changes/*/provenance.yml|*/.forge/changes/*/review.md)",
        "      printf '%s\\n' '{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"Forge review-control metadata (manifest.yml/provenance.yml/review.md) must not be mutated directly via Edit/Write; use the normal repository-native path so changes stay auditable (CHG-0018 FR-006, CHG-0045 FR-006).\"}}'",
        "      exit 0",
        "      ;;",
        "  esac",
        "  exit 0",
        "fi",
        "",
        "command=\"$(printf '%s' \"$input\" | jq -r '.tool_input.command // empty')\"",
        "",
        "if printf '%s' \"$command\" | grep -Eq "
        "'(sed[[:space:]]+-i|perl[[:space:]]+-i|truncate|>{1,2})[[:space:]]*"
        "[^&|;]{0,80}\\.forge/changes/[^[:space:]&|;]*"
        "(manifest\\.yml|provenance\\.yml|review\\.md)'",
        "then",
        "  printf '%s\\n' '{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"Forge review-control metadata (manifest.yml/provenance.yml/review.md) must not be mutated via shell redirection or in-place editing; use the normal Write/Edit tool path so changes stay auditable (CHG-0018 FR-006).\"}}'",
        "  exit 0",
        "fi",
        "exit 0",
    ))


def generate_claude_code_skill_bundle(
    *,
    contract_content: str,
    flows: Iterable[tuple[str, str]],
    protocol_id: int = 1,
    artifact_structure_content: str = "",
    decision_rules_content: str = "",
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
    has_decision_rules = bool(decision_rules_content)
    resources = (
        _resource(
            "skills/forge/SKILL.md",
            _skill_content(
                effective_flows,
                protocol_id,
                has_artifact_structure=has_artifact_structure,
                has_decision_rules=has_decision_rules,
                interaction_language=interaction_language,
            ),
        ),
        _resource("skills/forge/references/engineering-contract.md", contract_content),
        *(
            (_resource("skills/forge/references/artifact-structure.md", artifact_structure_content),)
            if has_artifact_structure
            else ()
        ),
        *(
            (_resource("skills/forge/references/decision-rules.md", decision_rules_content),)
            if has_decision_rules
            else ()
        ),
        _resource(_HOOK_RELATIVE_PATH, _hook_script_content(), executable=True),
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
        decision_rules_content=canonical.decision_rules_content,
        interaction_language=canonical.interaction_language,
    )
