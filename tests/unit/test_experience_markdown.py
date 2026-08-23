from typing import Any

from forge_cli.experience.markdown import render_markdown


def _report() -> dict[str, Any]:
    return {
        "schema": "forge/experience-report@1",
        "report": "FER-0012",
        "source": {
            "forge_version": "0.x.x",
            "protocol": 2,
            "change": "CHG-0030",
            "flow": "full",
            "adapter": "claude-code",
            "harness": "Claude Code",
            "repository": "forge-protocol",
            "commit": "abc123",
        },
        "observations": [
            {
                "id": "FER-0012-O001",
                "area": "plan-approval",
                "classification": "forge_problem",
                "expected": "The Harness should stop after Plan generation.",
                "observed": "The Harness continued into implementation.",
                "impact": "Human approval was bypassed.",
                "evidence": ["The Plan existed before implementation began."],
                "workaround": "The user manually interrupted the execution.",
                "follow_up": "Investigate mechanically verifiable Plan approval.",
            }
        ],
        "positive_evidence": [
            {
                "id": "FER-0012-P001",
                "area": "plan-scaffolding",
                "observed": "The generated Plan used the expected structure.",
            }
        ],
        "follow_up_candidates": [
            {
                "observation": "FER-0012-O001",
                "type": "investigation",
                "summary": "Investigate Plan approval enforcement.",
            }
        ],
    }


def test_render_markdown_projects_complete_report() -> None:
    rendered = render_markdown(_report())

    assert rendered == """<!-- Generated from the canonical Forge Experience Report. Do not edit manually. -->

# FER-0012

## Context
- Forge version: 0.x.x
- Protocol: 2
- Change: CHG-0030
- Flow: full
- Adapter: claude-code
- Harness: Claude Code
- Repository: forge-protocol
- Commit: abc123

## Summary
1 observation and 1 positive evidence entry were recorded.

## Observations

### FER-0012-O001 — plan-approval
**Classification**
Forge problem

**Expected**
The Harness should stop after Plan generation.

**Observed**
The Harness continued into implementation.

**Impact**
Human approval was bypassed.

**Evidence**
- The Plan existed before implementation began.

**Workaround**
The user manually interrupted the execution.

**Possible follow-up**
Investigate mechanically verifiable Plan approval.

## Positive Evidence

### FER-0012-P001 — plan-scaffolding
The generated Plan used the expected structure.

## Follow-up Candidates

- FER-0012-O001 — investigation: Investigate Plan approval enforcement.
"""


def test_render_markdown_omits_empty_optional_sections() -> None:
    report = _report()
    report["observations"] = []
    report["positive_evidence"] = []
    report["follow_up_candidates"] = []

    rendered = render_markdown(report)

    assert "## Summary" not in rendered
    assert "## Observations" not in rendered
    assert "## Positive Evidence" not in rendered
    assert "## Follow-up Candidates" not in rendered
    assert "Unknown" not in rendered


def test_render_markdown_is_deterministic() -> None:
    assert render_markdown(_report()) == render_markdown(_report())


def test_render_markdown_escapes_user_text_as_plain_text() -> None:
    report = _report()
    report["observations"][0]["observed"] = "# heading [link](https://example.test) *emphasis*"

    rendered = render_markdown(report)

    assert r"\# heading \[link\]\(https://example.test\) \*emphasis\*" in rendered


def test_render_markdown_preserves_canonical_order_and_multiline_text() -> None:
    report = _report()
    report["observations"].insert(
        0,
        {
            "id": "FER-0012-O000",
            "area": "first",
            "classification": "uncertain",
            "expected": "line one\nline two",
            "observed": "first observed",
            "evidence": ["first evidence"],
            "impact": "first impact",
        },
    )

    rendered = render_markdown(report)

    assert rendered.index("FER-0012-O000") < rendered.index("FER-0012-O001")
    assert "line one  \nline two" in rendered
