from pathlib import Path

from forge_cli.adapters.codex.projection import generate_codex_skill_bundle
from forge_cli.adapters.claude_code.projection import generate_claude_code_skill_bundle
from forge_cli.capabilities.loader import load_capability_catalog


def test_codex_projects_each_canonical_capability_as_a_discoverable_skill() -> None:
    root = Path(__file__).resolve().parents[2] / "capabilities"
    capabilities = load_capability_catalog(root)

    bundle = generate_codex_skill_bundle(
        contract_content="contract",
        flows=(("standard", "id: standard\n"),),
        capabilities=capabilities,
    )

    names = {resource.name for resource in bundle.resources}
    assert "investigate/SKILL.md" in names
    assert "investigate/references/CAPABILITY.md" in names
    assert "fix/SKILL.md" in names
    assert "qa/SKILL.md" in names

    investigate = next(item for item in bundle.resources if item.name == "investigate/SKILL.md")
    assert "references/CAPABILITY.md" in investigate.content
    assert "name: investigate" in investigate.content
    assert "slash" not in investigate.content.lower()


def test_claude_code_projects_the_same_catalog_without_redefining_behavior() -> None:
    root = Path(__file__).resolve().parents[2] / "capabilities"
    capabilities = load_capability_catalog(root)

    bundle = generate_claude_code_skill_bundle(
        contract_content="contract",
        flows=(("standard", "id: standard\n"),),
        capabilities=capabilities,
    )

    names = {resource.name for resource in bundle.resources}
    assert "skills/investigate/SKILL.md" in names
    assert "skills/investigate/references/CAPABILITY.md" in names
    skill = next(item for item in bundle.resources if item.name == "skills/investigate/SKILL.md")
    assert "sole source of competency behavior" in skill.content
