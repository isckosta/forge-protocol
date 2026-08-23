from pathlib import Path


ROOT = Path(__file__).parents[2]
WORKFLOW_TEMPLATES = (
    ROOT / "src/forge_cli/adapters/codex/resources/skills/workflow.md",
    ROOT / "src/forge_cli/adapters/claude_code/resources/skills/workflow.md",
)


def test_harness_workflows_require_branch_pr_and_resolved_comments() -> None:
    guidance = [path.read_text(encoding="utf-8") for path in WORKFLOW_TEMPLATES]

    for workflow in guidance:
        assert "create or use a working branch" in workflow
        assert "open a Pull Request against" in workflow
        assert "`main` and use that PR" in workflow
        assert "unresolved review comments" in workflow
        assert "must not" in workflow
        assert "merge or claim the Change complete" in workflow

    assert guidance[0] == guidance[1]
