from __future__ import annotations

from forge_cli.adapters.claude_code import projection
from forge_cli.adapters.claude_code.projection import (
    ClaudeCodeProjectionInput,
    generate_claude_code_projection_bundle,
)


def test_projection_uses_packaged_workflow_template() -> None:
    loader = getattr(projection, "load_workflow_skill_template", None)
    assert loader is not None, "Packaged workflow template is not connected to projection yet"

    template = loader().strip()
    bundle = generate_claude_code_projection_bundle(
        ClaudeCodeProjectionInput(
            flow_id="full",
            flow_content="stages:\n  - id: verification\n",
            contract_content="canonical contract",
        )
    )
    skill = next(item for item in bundle.resources if item.name == "skills/forge/SKILL.md")

    assert template
    assert template in skill.content
    assert "may not refresh its skill catalog in the current session" in skill.content
    assert "Harness runtime behavior, not technically controlled by Forge" in skill.content


def test_workflow_template_instructs_checking_adapter_drift_before_trusting_references() -> None:
    """CHG-0045 FR-004/TDD-007: an agent must check the existing digest-based
    drift signal (forge doctor / forge adapter doctor) before relying on
    references/*, and must stop and report rather than silently self-heal."""
    template = projection.load_workflow_skill_template()
    assert "forge doctor" in template or "forge adapter doctor" in template
    assert "drift" in template.lower()
    assert "stop" in template.lower() or "report" in template.lower()


def test_workflow_template_instructs_boundary_reporting_format() -> None:
    """CHG-0045 FR-007/TDD-013: a human-authority/blocked/missing-evidence
    boundary report must name Change, Flow, State, Boundary, Required
    Decision/Evidence, and Next Permitted Action."""
    template = projection.load_workflow_skill_template()
    for term in (
        "Current Change",
        "Effective Flow",
        "Current State",
        "Boundary",
        "Next Permitted Action",
    ):
        assert term in template, f"workflow.md is missing boundary-report element {term!r}"
