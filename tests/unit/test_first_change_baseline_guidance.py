from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).parents[2]
CODEX_WORKFLOW = ROOT / "src/forge_cli/adapters/codex/resources/skills/workflow.md"
CLAUDE_WORKFLOW = ROOT / "src/forge_cli/adapters/claude_code/resources/skills/workflow.md"
SHARED_CONTRACT = ROOT / "protocol/contract/engineering.md"
PROTOCOL_2_CONTRACT = ROOT / "protocol/versions/2/contract/engineering.md"

BASELINE_GUIDANCE = "When this is the repository's first commit"
BASELINE_REQUIREMENT = "complete pre-existing state in the intended repository scope, with no file excluded"
NON_ENFORCEMENT = "This Adapter projects the requirement but cannot technically enforce Git behavior"
C076_MARKER = "C-076 — Complete baseline for a first-commit Change"


def test_codex_workflow_explicitly_guides_first_commit_baseline() -> None:
    content = CODEX_WORKFLOW.read_text(encoding="utf-8")

    assert BASELINE_GUIDANCE in content
    assert BASELINE_REQUIREMENT in " ".join(content.split())
    assert NON_ENFORCEMENT in " ".join(content.split())


def test_claude_code_workflow_explicitly_guides_first_commit_baseline() -> None:
    content = CLAUDE_WORKFLOW.read_text(encoding="utf-8")

    assert BASELINE_GUIDANCE in content
    assert BASELINE_REQUIREMENT in " ".join(content.split())
    assert NON_ENFORCEMENT in " ".join(content.split())


def test_workflow_templates_project_identical_baseline_guidance() -> None:
    codex = CODEX_WORKFLOW.read_text(encoding="utf-8")
    claude = CLAUDE_WORKFLOW.read_text(encoding="utf-8")

    normalized_codex = " ".join(codex.split())
    normalized_claude = " ".join(claude.split())
    codex_block = normalized_codex[normalized_codex.index(BASELINE_GUIDANCE) : normalized_codex.index(NON_ENFORCEMENT) + len(NON_ENFORCEMENT)]
    claude_block = normalized_claude[normalized_claude.index(BASELINE_GUIDANCE) : normalized_claude.index(NON_ENFORCEMENT) + len(NON_ENFORCEMENT)]
    assert codex_block == claude_block


def test_both_effective_contracts_define_the_same_first_commit_rule() -> None:
    shared = SHARED_CONTRACT.read_text(encoding="utf-8")
    protocol_2 = PROTOCOL_2_CONTRACT.read_text(encoding="utf-8")

    assert C076_MARKER in shared
    assert C076_MARKER in protocol_2
    shared_rule = shared[shared.index(C076_MARKER) :]
    protocol_2_rule = protocol_2[protocol_2.index(C076_MARKER) :]
    assert shared_rule == protocol_2_rule
