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
