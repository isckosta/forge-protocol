from __future__ import annotations

import re

import pytest
import yaml

from forge_cli.adapters.claude_code.projection import (
    ClaudeCodeProjectionInput,
    generate_claude_code_projection_bundle,
)
from forge_cli.adapters.codex.projection import (
    CodexProjectionInput,
    generate_codex_projection_bundle,
)


_EXPECTED_DESCRIPTION = (
    "Use in a Forge-enabled repository when the request involves a material "
    "software change: implementing or materially changing behavior, fixing a "
    "material defect, continuing an existing Forge Change, or explicitly "
    "requesting Forge governance. Do not activate for questions, explanations, "
    "reading, investigation without a change, trivial operations, or immaterial edits."
)


@pytest.fixture(params=("codex", "claude-code"))
def projected_skill(request: pytest.FixtureRequest) -> str:
    if request.param == "codex":
        bundle = generate_codex_projection_bundle(
            CodexProjectionInput(
                flow_id="standard",
                flow_content="stages:\n  - id: verification\n",
                contract_content="canonical contract",
            )
        )
        return next(resource.content for resource in bundle.resources if resource.name == "SKILL.md")

    bundle = generate_claude_code_projection_bundle(
        ClaudeCodeProjectionInput(
            flow_id="standard",
            flow_content="stages:\n  - id: verification\n",
            contract_content="canonical contract",
        )
    )
    return next(
        resource.content
        for resource in bundle.resources
        if resource.name == "skills/forge/SKILL.md"
    )


def _description(skill: str) -> str:
    return yaml.safe_load(skill.split("---", 2)[1])["description"]


def test_all_harness_projections_publish_the_same_observable_activation_contract(
    projected_skill: str,
) -> None:
    assert _description(projected_skill) == _EXPECTED_DESCRIPTION


@pytest.mark.parametrize(
    "observable_signal",
    (
        "implementing or materially changing behavior",
        "fixing a material defect",
        "continuing an existing Forge Change",
        "explicitly requesting Forge governance",
    ),
)
def test_activation_description_contains_each_positive_routing_signal(
    projected_skill: str, observable_signal: str
) -> None:
    assert observable_signal in _description(projected_skill)


@pytest.mark.parametrize(
    "non_trigger",
    (
        "questions",
        "explanations",
        "reading",
        "investigation without a change",
        "trivial operations",
        "immaterial edits",
    ),
)
def test_activation_description_excludes_non_change_work(
    projected_skill: str, non_trigger: str
) -> None:
    assert non_trigger in _description(projected_skill)


def test_ambiguous_materiality_is_routed_by_the_observable_change_signal() -> None:
    description = _EXPECTED_DESCRIPTION
    assert "material software change" in description
    assert "immaterial edits" in description
    assert "Forge-governed engineering Changes" not in description
