from __future__ import annotations

from forge_cli.adapters.codex import projection
from forge_cli.adapters.codex.projection import CodexProjectionInput, generate_codex_projection_bundle


def test_projection_uses_packaged_workflow_template() -> None:
    loader = getattr(projection, "load_workflow_skill_template", None)
    assert loader is not None, "Packaged workflow template is not connected to projection yet"

    template = loader().strip()
    bundle = generate_codex_projection_bundle(
        CodexProjectionInput(
            flow_id="full",
            flow_content="stages:\n  - id: verification\n",
            contract_content="canonical contract",
        )
    )
    flow = next(item for item in bundle.resources if item.name == "forge-flow.md")

    assert template
    assert template in flow.content
