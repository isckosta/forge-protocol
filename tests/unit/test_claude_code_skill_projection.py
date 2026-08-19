from __future__ import annotations

from hashlib import sha256
import re

import yaml

from forge_cli.adapters.claude_code.driver import ClaudeCodeDriver
from forge_cli.adapters.driver import AdapterProjectionContext


FLOW = """schema: forge/flow@1
flow:
  id: {flow_id}
stages:
  - id: tdd_implementation
  - id: verification
  - id: strict_review
gates:
  before_behavioral_implementation:
    checks: [red_executed, red_failed_for_expected_reason]
"""


def _context(*, flows: tuple[str, ...] = ("standard", "full")) -> AdapterProjectionContext:
    return AdapterProjectionContext(
        project_protocol=1,
        flows=tuple((flow_id, FLOW.format(flow_id=flow_id)) for flow_id in flows),
        contract_content="# Engineering Contract\nCanonical contract text.\n",
        target=".claude",
    )


def test_claude_code_projection_renders_a_valid_repository_layout() -> None:
    """A missing or misplaced resource must fail this contract."""
    projection = ClaudeCodeDriver().project(_context())
    by_path = {item.path: item.content for item in projection.artifacts}

    assert tuple(sorted(by_path)) == (
        ".claude/CLAUDE.md",
        ".claude/skills/forge/SKILL.md",
        ".claude/skills/forge/hooks/check-manifest-edit.sh",
        ".claude/skills/forge/references/engineering-contract.md",
        ".claude/skills/forge/references/flows/full.yml",
        ".claude/skills/forge/references/flows/standard.yml",
    )
    skill = by_path[".claude/skills/forge/SKILL.md"]
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    assert metadata["name"] == "forge"
    assert metadata["description"] == "Use for Forge-governed engineering Changes in this repository."
    assert metadata["hooks"]["PreToolUse"][0]["matcher"] == "Bash"
    assert "Repository-native Forge state remains authoritative." in skill


def test_claude_code_projection_keeps_effective_inputs_in_references_and_is_deterministic() -> None:
    """A renderer that leaks inputs into SKILL.md or depends on ordering must fail."""
    context = _context(flows=("full", "standard"))

    first = ClaudeCodeDriver().project(context)
    second = ClaudeCodeDriver().project(context)
    first_by_path = {item.path: item.content for item in first.artifacts}

    assert first == second
    assert tuple(item.path for item in first.artifacts) == tuple(
        sorted(item.path for item in first.artifacts)
    )
    assert all(item.content.endswith("\n") and not item.content.endswith("\n\n") for item in first.artifacts)
    assert all(
        sha256(item.content.encode("utf-8")).hexdigest()
        == sha256(second_item.content.encode("utf-8")).hexdigest()
        for item, second_item in zip(first.artifacts, second.artifacts, strict=True)
    )
    skill = first_by_path[".claude/skills/forge/SKILL.md"]
    assert "Canonical contract text." not in skill
    assert "id: full" not in skill
    assert "Canonical contract text." in first_by_path[
        ".claude/skills/forge/references/engineering-contract.md"
    ]
    assert "id: full" in first_by_path[".claude/skills/forge/references/flows/full.yml"]


def test_claude_code_skill_links_only_the_effective_contract_and_flows_deterministically() -> None:
    """Removing a skill reference link must make its generated artifact unreachable."""
    first = ClaudeCodeDriver().project(_context(flows=("standard", "full")))
    reordered = ClaudeCodeDriver().project(_context(flows=("full", "standard")))
    first_skill = next(item.content for item in first.artifacts if item.path.endswith("SKILL.md"))
    reordered_skill = next(item.content for item in reordered.artifacts if item.path.endswith("SKILL.md"))

    assert first_skill == reordered_skill
    assert """## Effective Forge references

- [Engineering Contract](references/engineering-contract.md)
- [Flow `full`](references/flows/full.yml)
- [Flow `standard`](references/flows/standard.yml)
""" in first_skill
    assert re.findall(r"\[[^]]+\]\((references/[^)]+)\)", first_skill) == [
        "references/engineering-contract.md",
        "references/flows/full.yml",
        "references/flows/standard.yml",
    ]


def test_claude_code_projection_includes_artifact_structure_reference_when_present() -> None:
    without = ClaudeCodeDriver().project(_context())
    without_paths = {item.path for item in without.artifacts}
    assert ".claude/skills/forge/references/artifact-structure.md" not in without_paths

    context = AdapterProjectionContext(
        project_protocol=1,
        flows=(("standard", FLOW.format(flow_id="standard")),),
        contract_content="# Engineering Contract\nCanonical contract text.\n",
        artifact_structure_content="# Canonical Artifact Structure\nProgressive Disclosure.\n",
        target=".claude",
    )
    projection = ClaudeCodeDriver().project(context)
    by_path = {item.path: item.content for item in projection.artifacts}

    assert ".claude/skills/forge/references/artifact-structure.md" in by_path
    assert "Progressive Disclosure" in by_path[
        ".claude/skills/forge/references/artifact-structure.md"
    ]
    skill = by_path[".claude/skills/forge/SKILL.md"]
    assert "Progressive Disclosure" not in skill
    assert "references/artifact-structure.md" in skill


def test_claude_code_projection_renders_effective_interaction_language() -> None:
    explicit = ClaudeCodeDriver().project(
        AdapterProjectionContext(
            project_protocol=1,
            flows=(("standard", FLOW.format(flow_id="standard")),),
            contract_content="# Engineering Contract\nCanonical contract text.\n",
            target=".claude",
            interaction_language="pt-BR",
        )
    )
    explicit_skill = next(
        item.content for item in explicit.artifacts if item.path.endswith("SKILL.md")
    )
    assert "Interaction language: pt-BR" in explicit_skill

    default = ClaudeCodeDriver().project(_context())
    default_skill = next(
        item.content for item in default.artifacts if item.path.endswith("SKILL.md")
    )
    assert "Interaction language: auto" in default_skill


def test_claude_code_projection_reports_no_technically_enforced_gates_as_generic_limitations() -> None:
    """Codex-parity check: neither Adapter claims technical enforcement of
    TDD/Strict Review via the `skills` capability -- the hook (FR-006) is
    a separate, narrow, explicitly-scoped mechanism, not a blanket
    enforcement claim over these two invariants."""
    projection = ClaudeCodeDriver().project(_context())

    assert tuple((item.requirement_id, item.capability, item.enforced) for item in projection.limitations) == (
        ("strict-review", "skills", False),
        ("tdd-red-before-behavior", "skills", False),
    )
    assert projection.representation.repository_authority_preserved is True
    assert projection.representation.red_before_behavior_preserved is True
    assert projection.representation.strict_review_preserved is True


def test_claude_code_projection_does_not_claim_red_gate_from_tdd_stage_alone() -> None:
    incomplete_flow = FLOW.replace(
        "checks: [red_executed, red_failed_for_expected_reason]",
        "checks: [red_executed]",
    )
    context = AdapterProjectionContext(
        project_protocol=1,
        flows=(("standard", incomplete_flow.format(flow_id="standard")),),
        contract_content="contract",
        target=".claude",
    )

    projection = ClaudeCodeDriver().project(context)

    assert projection.representation.red_before_behavior_preserved is False
    assert "tdd-red-before-behavior" not in projection.representation.represented_invariants
    assert "tdd-red-before-behavior" in {
        limitation.requirement_id for limitation in projection.limitations
    }
