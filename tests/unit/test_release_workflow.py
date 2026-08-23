from pathlib import Path


WORKFLOW = Path(__file__).parents[2] / ".github" / "workflows" / "publish.yml"


def test_release_workflow_requires_merged_pr_provenance_before_build() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "release-provenance:" in workflow
    assert "listPullRequestsAssociatedWithCommit" in workflow
    assert "pull.base.ref === \"main\"" in workflow
    assert "pull.merged_at" in workflow
    assert "git merge-base --is-ancestor" in workflow
    assert "needs: release-provenance" in workflow
