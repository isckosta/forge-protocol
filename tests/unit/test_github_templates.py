from pathlib import Path


GITHUB = Path(__file__).parents[2] / ".github"


def test_pull_request_template_uses_forge_review_structure() -> None:
    template = (GITHUB / "pull_request_template.md").read_text(encoding="utf-8")

    for heading in (
        "## Change",
        "## Intent",
        "## Scope",
        "## Verification",
        "## Forge Status",
        "## Documentation Impact",
    ):
        assert heading in template
    assert "## Checklist" in template


def test_issue_templates_capture_problem_and_scope() -> None:
    bug = (GITHUB / "ISSUE_TEMPLATE" / "bug-report.md").read_text(encoding="utf-8")
    change = (GITHUB / "ISSUE_TEMPLATE" / "change-request.md").read_text(encoding="utf-8")

    for template in (bug, change):
        assert template.startswith("---\n")
        assert "## Problem" in template
        assert "## Impact" in template
        assert "## Scope" in template
        assert "## Out of Scope" in template
        assert "## Evidence" in template
