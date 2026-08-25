import pytest

from forge_cli.merge_readiness.policy import classify_path, load_materiality_policy


_ADAPTER_GENERATED_PATHS = [
    ".claude/CLAUDE.md",
    ".claude/skills/forge/SKILL.md",
    ".claude/skills/forge/hooks/check-manifest-edit.sh",
    ".claude/skills/forge/references/artifact-structure.md",
    ".claude/skills/forge/references/engineering-contract.md",
    ".agents/skills/forge/SKILL.md",
    ".agents/skills/forge/references/artifact-structure.md",
    ".agents/skills/forge/references/engineering-contract.md",
    ".forge/adapters/claude-code/installation.yml",
    ".forge/adapters/codex/installation.yml",
]


@pytest.mark.parametrize("path", _ADAPTER_GENERATED_PATHS)
def test_agent_adapter_generated_paths_resolve_to_a_definite_classification(path: str) -> None:
    """TDD-004 / AC-004: the ten Agent Adapter-generated paths Discovery
    identified (CHG-0046) must resolve to material, never ambiguous —
    MR-017 currently blocks every PR that touches generated Adapter
    output, including CHG-0045's own PR #36."""
    policy = load_materiality_policy()
    assert classify_path(path, policy) == "material"


def test_unrelated_unclassified_path_still_falls_back_to_ambiguous() -> None:
    """TDD-005 / AC-005: adding the ten scoped rules above must not loosen
    classify_path's fail-closed default for anything else."""
    policy = load_materiality_policy()
    assert classify_path("unclassified.data", policy) == "ambiguous"
