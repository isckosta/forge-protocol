"""CHG-0022 TDD-001..003: Change scaffold planning and rendering."""

from pathlib import Path

import pytest
import yaml
from jsonschema import validate

from forge_cli.change_scaffolding import (
    allocate_change_number,
    render_scaffold,
    validate_slug,
)


PROTOCOL_ROOT = Path(__file__).parents[2] / "protocol"


def _canonical_flow(flow_id: str) -> dict:
    return yaml.safe_load(
        (PROTOCOL_ROOT / "flows" / f"{flow_id}.yml").read_text(encoding="utf-8")
    )


@pytest.mark.parametrize(
    "slug",
    ["", "Bad", "two--hyphens", "-leading", "trailing-", "café", "../escape", "a_b"],
)
def test_validate_slug_rejects_non_canonical_values(slug: str) -> None:
    with pytest.raises(ValueError):
        validate_slug(slug)


@pytest.mark.parametrize("slug", ["fix", "api-v2", "v2-change-9"])
def test_validate_slug_accepts_lowercase_ascii_segments(slug: str) -> None:
    assert validate_slug(slug) == slug


def test_allocate_change_number_scans_existing_canonical_directories(tmp_path: Path) -> None:
    changes = tmp_path / ".forge" / "changes"
    changes.mkdir(parents=True)
    for name in ("CHG-0003-old", "CHG-0021-latest", "not-a-change", "CHG-x-invalid"):
        (changes / name).mkdir()

    assert allocate_change_number(changes) == 22


@pytest.mark.parametrize(
    ("flow_id", "behavioral", "expected_paths"),
    [
        (
            "fast",
            True,
            {"intent.md", "inspection.md", "test-design.md", "tdd-evidence.yml", "verification.md", "review.md", "manifest.yml"},
        ),
        (
            "fast",
            False,
            {"intent.md", "inspection.md", "verification.md", "review.md", "manifest.yml"},
        ),
        (
            "standard",
            True,
            {"intent.md", "discovery.md", "specification.md", "test-design.md", "plan.md", "tdd-evidence.yml", "verification.md", "review.md", "manifest.yml"},
        ),
        (
            "full",
            True,
            {"intent.md", "discovery.md", "specification.md", "specification-review.md", "architecture.md", "test-strategy.md", "plan.md", "tasks.md", "tdd-evidence.yml", "verification.md", "review.md", "knowledge-capture.md", "manifest.yml"},
        ),
        (
            "full",
            False,
            {"intent.md", "discovery.md", "specification.md", "specification-review.md", "architecture.md", "test-strategy.md", "plan.md", "tasks.md", "verification.md", "review.md", "knowledge-capture.md", "manifest.yml"},
        ),
    ],
)
def test_render_scaffold_uses_only_the_selected_flow_stages(
    flow_id: str, behavioral: bool, expected_paths: set[str]
) -> None:
    plan = render_scaffold(
        change_id="CHG-0022",
        slug="sample-change",
        flow_id=flow_id,
        flow_data=_canonical_flow(flow_id),
        behavioral=behavioral,
    )

    assert set(plan.files) == expected_paths
    assert list(plan.files)[-1] == "manifest.yml"


def test_render_scaffold_markdown_has_frontmatter_and_yaml_has_schema() -> None:
    plan = render_scaffold(
        change_id="CHG-0022",
        slug="api-v2-fix",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    for path, content in plan.files.items():
        if path.endswith(".md"):
            assert content.startswith("---\nforge:\n")
            assert "change: CHG-0022" in content
        else:
            data = yaml.safe_load(content)
            assert isinstance(data, dict)
            if path == "manifest.yml":
                assert data["change"]["id"] == "CHG-0022"
            else:
                assert data["change"] == "CHG-0022"


def test_render_scaffold_intent_uses_structured_human_facing_layout() -> None:
    plan = render_scaffold(
        change_id="CHG-0042",
        slug="stock-reservation-on-sales-order-confirmation",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )
    intent = plan.files["intent.md"]

    assert intent.startswith(
        "---\nforge:\n  artifact: intent\n  schema: 1\n"
        "change: CHG-0042\nstatus: active\n---\n\n"
        "# CHG-0042 · Stock Reservation On Sales Order Confirmation\n\n"
        "> **Change Intent**\n"
    )
    assert "## Overview\n| | |\n|---|---|\n| **Change** | CHG-0042 |" in intent
    assert "| **Flow** | STANDARD |" in intent
    assert "| **Status** | Active |" in intent
    for heading in ("Problem", "Goal", "Scope", "Out of Scope", "Success Criteria"):
        assert f"## {heading}" in intent
    for heading in (
        "Summary",
        "Desired Outcome",
        "Non-goals",
        "FR-001",
        "AC-001",
    ):
        assert heading not in intent


def test_render_scaffold_intent_does_not_emit_conditional_empty_sections() -> None:
    plan = render_scaffold(
        change_id="CHG-0042",
        slug="http-timeout-retry-policy",
        flow_id="fast",
        flow_data=_canonical_flow("fast"),
        behavioral=False,
    )

    intent = plan.files["intent.md"]
    for heading in (
        "Business Impact",
        "Current Behavior",
        "Desired Behavior",
        "Expected Outcome",
        "Business Rules",
        "Operational Boundary",
    ):
        assert f"## {heading}" not in intent


@pytest.mark.parametrize("flow_id", ["fast", "full"])
def test_render_scaffold_intent_derives_only_core_metadata(flow_id: str) -> None:
    plan = render_scaffold(
        change_id="CHG-0042",
        slug="metadata-safe-intent",
        flow_id=flow_id,
        flow_data=_canonical_flow(flow_id),
        behavioral=True,
    )

    intent = plan.files["intent.md"]
    assert f"| **Flow** | {flow_id.upper()} |" in intent
    assert "| **Status** | Active |" in intent
    assert "Domain" not in intent
    assert "Primary Module" not in intent
    assert "Business Risk" not in intent


def test_render_scaffold_manifest_matches_change_schema() -> None:
    plan = render_scaffold(
        change_id="CHG-0022",
        slug="api-v2-fix",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )
    manifest = yaml.safe_load(plan.files["manifest.yml"])
    schema = yaml.safe_load(
        (PROTOCOL_ROOT / "schemas" / "change-v2.schema.json").read_text(encoding="utf-8")
    )

    validate(instance=manifest, schema=schema)
    assert manifest["change"]["title"] == "Api V2 Fix"
    assert manifest["review"]["iteration"] == 0
    assert manifest["review"]["iterations"] == []
    assert manifest["tdd"]["status"] == "pending"
    assert "decisions" not in manifest


def test_render_scaffold_specification_uses_traceable_contract_layout() -> None:
    plan = render_scaffold(
        change_id="CHG-0037",
        slug="specification-layout",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    specification = plan.files["specification.md"]

    assert specification.startswith(
        "---\nforge:\n  artifact: specification\n  schema: 1\n"
        "change: CHG-0037\nstatus: pending\n---\n\n"
        "# CHG-0037 · Specification\n\n"
        "> **Change Contract**\n"
    )
    for heading in (
        "Overview",
        "User Stories",
        "Functional Requirements",
        "Non-functional Requirements",
        "Constraints",
        "Traceability Matrix",
        "Compatibility Statement",
        "Specification Gate",
    ):
        assert f"## {heading}" in specification
    assert "### US-001" not in specification
    assert "### FR-001" in specification
    assert "#### Requirement" in specification
    assert "#### Acceptance" in specification
    assert "Acceptance Criteria" not in specification


def test_render_scaffold_specification_explains_optional_user_stories() -> None:
    plan = render_scaffold(
        change_id="CHG-0037",
        slug="technical-maintenance",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=False,
    )

    specification = plan.files["specification.md"]

    assert "User Stories are optional" in specification
    assert "Requirement without a User Story is valid" in specification
    assert "As a user" not in specification


def test_render_scaffold_test_design_uses_verification_design_contract_layout() -> None:
    plan = render_scaffold(
        change_id="CHG-0038",
        slug="test-design-layout",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    test_design = plan.files["test-design.md"]

    assert test_design.startswith(
        "---\nforge:\n  artifact: test_design\n  schema: 1\n"
        "change: CHG-0038\nstatus: pending\n---\n\n"
        "# CHG-0038 · Test Design\n\n"
        "> Verification Design\n"
    )
    for heading in (
        "Overview",
        "Test Strategy",
        "Coverage Map",
        "Requirement Coverage",
        "Coverage Gaps",
        "Test Design Gate",
    ):
        assert f"## {heading}" in test_design
    for legacy in ("## Objective", "## Strategy", "TDD-001 — <behavior>", "## Completion Criteria"):
        assert legacy not in test_design


def test_render_scaffold_test_design_scenario_is_self_contained_and_not_padded() -> None:
    plan = render_scaffold(
        change_id="CHG-0038",
        slug="test-design-scenario",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    test_design = plan.files["test-design.md"]

    assert "### TD-001 ·" in test_design
    for subheading in ("Purpose", "Preconditions", "Scenario", "Evidence", "Failure Condition", "Boundary"):
        assert f"#### {subheading}" in test_design
    assert "N/A" not in test_design


def test_render_scaffold_test_design_explains_optional_user_stories() -> None:
    plan = render_scaffold(
        change_id="CHG-0038",
        slug="test-design-technical",
        flow_id="fast",
        flow_data=_canonical_flow("fast"),
        behavioral=True,
    )

    test_design = plan.files["test-design.md"]

    assert "Requirement without a User Story is valid" in test_design
    assert "### US-001" not in test_design


def test_render_scaffold_test_design_separates_manual_acceptance() -> None:
    plan = render_scaffold(
        change_id="CHG-0038",
        slug="test-design-manual",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    test_design = plan.files["test-design.md"]

    assert "Manual Acceptance" in test_design
    assert "Preconditions" in test_design
    assert "operator instructions" in test_design
    assert "MUST NOT be presented as an automated guarantee" in test_design


def test_render_scaffold_test_design_defines_valid_red() -> None:
    plan = render_scaffold(
        change_id="CHG-0038",
        slug="test-design-red",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    test_design = plan.files["test-design.md"]

    assert "fails for the expected behavioral reason" in test_design
    for cause in ("syntax error", "broken import", "invalid fixture", "infrastructure unavailability"):
        assert cause in test_design


def test_render_scaffold_test_strategy_template_is_unchanged() -> None:
    plan = render_scaffold(
        change_id="CHG-0038",
        slug="test-strategy-unaffected",
        flow_id="full",
        flow_data=_canonical_flow("full"),
        behavioral=True,
    )

    test_strategy = plan.files["test-strategy.md"]

    assert test_strategy.endswith(
        "## Objective\n\nState the test strategy objective.\n\n## Strategy\n\n"
        "## TDD-001 — <behavior>\n\nDefine the test case.\n\n"
        "## Completion Criteria\n\nList completion criteria.\n"
    )


def test_render_scaffold_plan_template_is_unchanged() -> None:
    plan = render_scaffold(
        change_id="CHG-0039",
        slug="plan-unaffected",
        flow_id="full",
        flow_data=_canonical_flow("full"),
        behavioral=True,
    )

    assert plan.files["plan.md"].endswith(
        "1. Describe the first approved work item and files.\n\n"
        "## Implementation Boundary\n\n"
        "Reaching `plan_complete` is not authorization to begin Implementation.\n"
    )


def test_render_scaffold_tasks_uses_grouped_execution_checklist_layout() -> None:
    plan = render_scaffold(
        change_id="CHG-0042",
        slug="tasks-layout",
        flow_id="full",
        flow_data=_canonical_flow("full"),
        behavioral=True,
    )

    tasks = plan.files["tasks.md"]

    assert tasks.startswith(
        "---\nforge:\n  artifact: tasks\n  schema: 1\n"
        "change: CHG-0042\nstatus: pending\n---\n\n"
        "# CHG-0042 · Tasks\n\n"
        "> Execution Checklist\n"
    )
    for heading in ("Overview", "Execution", "Status"):
        assert f"## {heading}" in tasks
    assert "- [ ] T-001 <work item>\n\n## Status\n\nNo task has started.\n" not in tasks


def test_render_scaffold_tasks_groups_by_plan_item() -> None:
    plan = render_scaffold(
        change_id="CHG-0042",
        slug="tasks-plan-grouping",
        flow_id="full",
        flow_data=_canonical_flow("full"),
        behavioral=True,
    )

    tasks = plan.files["tasks.md"]

    assert "### Plan 1 ·" in tasks
    plan_section = tasks.split("### Plan 1 ·", 1)[1]
    assert "- [ ] T-001" in plan_section


def test_render_scaffold_tasks_has_compact_optional_traceability() -> None:
    plan = render_scaffold(
        change_id="CHG-0042",
        slug="tasks-traceability",
        flow_id="full",
        flow_data=_canonical_flow("full"),
        behavioral=True,
    )

    tasks = plan.files["tasks.md"]

    assert "`Plan: 1`" in tasks
    assert "`Requirements: FR-001`" in tasks
    assert "`Test Design: TDD-001`" in tasks
    assert "not every Task needs every reference" in tasks


def test_render_scaffold_tasks_overview_and_status_are_compact() -> None:
    plan = render_scaffold(
        change_id="CHG-0042",
        slug="tasks-overview-status",
        flow_id="full",
        flow_data=_canonical_flow("full"),
        behavioral=True,
    )

    tasks = plan.files["tasks.md"]

    assert "## Overview\n| | |\n|---|---|\n| **Change** | CHG-0042 |" in tasks
    assert "| **Flow** | FULL |" in tasks
    assert tasks.rstrip().endswith("No task has started.")
    last_heading = [line for line in tasks.splitlines() if line.startswith("## ")][-1]
    assert last_heading == "## Status"


def test_render_scaffold_verification_uses_result_first_coverage_layout() -> None:
    plan = render_scaffold(
        change_id="CHG-0040",
        slug="verification-layout",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    verification = plan.files["verification.md"]

    assert verification.startswith(
        "---\nforge:\n  artifact: verification\n  schema: 1\n"
        "change: CHG-0040\nstatus: pending\n---\n\n"
        "# CHG-0040 · Verification\n\n"
    )
    expected_order = [
        "## Result",
        "## Summary",
        "## Acceptance Coverage",
        "## Requirement Coverage",
        "## Test Evidence",
        "## Forge Evidence",
        "## Manual Evidence",
        "## Compatibility and Limitations",
        "## Conclusion",
    ]
    headings = [line for line in verification.splitlines() if line.startswith("## ")]
    assert headings == expected_order
    assert "Record verification results." not in verification


def test_render_scaffold_verification_result_placeholder_is_distinct_from_recognized_states() -> None:
    plan = render_scaffold(
        change_id="CHG-0040",
        slug="verification-result",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    verification = plan.files["verification.md"]
    result_section = verification.split("## Result", 1)[1].split("## Summary", 1)[0]

    assert "**PENDING**" in result_section
    assert "#" not in result_section
    for state in ("PASS", "FAIL", "SKIPPED", "NOT APPLICABLE", "INCONCLUSIVE"):
        assert state not in result_section


def test_render_scaffold_verification_acceptance_coverage_is_compact_and_id_referencing() -> None:
    plan = render_scaffold(
        change_id="CHG-0040",
        slug="verification-acceptance-coverage",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    verification = plan.files["verification.md"]

    assert "| Acceptance | Requirement | Result | Evidence |" in verification
    assert "do not reproduce its full text here" in verification


def test_render_scaffold_verification_requirement_coverage_is_conditional() -> None:
    plan = render_scaffold(
        change_id="CHG-0040",
        slug="verification-requirement-coverage",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    verification = plan.files["verification.md"]

    assert "Omit this section when Acceptance Coverage already expresses per-Requirement coverage" in verification


def test_render_scaffold_verification_manual_evidence_is_distinct() -> None:
    plan = render_scaffold(
        change_id="CHG-0040",
        slug="verification-manual-evidence",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    verification = plan.files["verification.md"]

    assert "## Manual Evidence" in verification
    assert "only when a real manual verification occurred" in verification
    manual_index = verification.index("## Manual Evidence")
    test_evidence_index = verification.index("## Test Evidence")
    forge_evidence_index = verification.index("## Forge Evidence")
    assert test_evidence_index < forge_evidence_index < manual_index


def test_render_scaffold_verification_test_evidence_references_tdd_by_id() -> None:
    plan = render_scaffold(
        change_id="CHG-0040",
        slug="verification-tdd-reference",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    verification = plan.files["verification.md"]

    assert "TDD-xxx" in verification
    assert "instead of renarrating the sequence" in verification


def test_render_scaffold_verification_conclusion_does_not_imply_completion_under_fail() -> None:
    plan = render_scaffold(
        change_id="CHG-0040",
        slug="verification-conclusion",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    verification = plan.files["verification.md"]

    assert "Do not imply Completion when Result is FAIL or SKIPPED" in verification
    assert "Review remains pending" in verification


def test_render_scaffold_verification_prompts_for_skipped_or_not_applicable_rationale() -> None:
    plan = render_scaffold(
        change_id="CHG-0040",
        slug="verification-skipped-rationale",
        flow_id="standard",
        flow_data=_canonical_flow("standard"),
        behavioral=True,
    )

    verification = plan.files["verification.md"]

    assert "SKIPPED or NOT APPLICABLE" in verification
    assert "rationale" in verification


def test_render_scaffold_verification_acceptance_coverage_evidence_placeholder_is_neutral() -> None:
    plan = render_scaffold(
        change_id="CHG-0040",
        slug="verification-evidence-placeholder",
        flow_id="fast",
        flow_data=_canonical_flow("fast"),
        behavioral=False,
    )

    verification = plan.files["verification.md"]

    assert "TDD-001" not in verification
    assert "TD-001" not in verification


def test_render_scaffold_review_plan_test_strategy_tasks_templates_are_unchanged() -> None:
    plan = render_scaffold(
        change_id="CHG-0040",
        slug="verification-unaffected-templates",
        flow_id="full",
        flow_data=_canonical_flow("full"),
        behavioral=True,
    )

    assert plan.files["review.md"].endswith(
        "## Verdict\n\n**PENDING**\n\n## Iteration 1 — PENDING\n\nRecord Strict Review findings.\n"
    )
    assert plan.files["plan.md"].endswith(
        "1. Describe the first approved work item and files.\n\n"
        "## Implementation Boundary\n\n"
        "Reaching `plan_complete` is not authorization to begin Implementation.\n"
    )
    assert plan.files["test-strategy.md"].endswith(
        "## Objective\n\nState the test strategy objective.\n\n## Strategy\n\n"
        "## TDD-001 — <behavior>\n\nDefine the test case.\n\n"
        "## Completion Criteria\n\nList completion criteria.\n"
    )
    assert "No task has started." in plan.files["tasks.md"]
