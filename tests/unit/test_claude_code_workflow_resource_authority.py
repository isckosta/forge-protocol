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
