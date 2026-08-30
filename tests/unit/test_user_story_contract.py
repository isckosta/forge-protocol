"""CHG-0050: semantic User Story obligation and stable story traceability."""

from pathlib import Path

from forge_cli.validation import (
    _validate_all_user_story_contracts,
    _validate_all_user_story_traceability,
)


def _write_change(root: Path, *, observable: bool, specification: str) -> Path:
    change = root / ".forge" / "changes" / "CHG-0050-example"
    change.mkdir(parents=True)
    (change / "manifest.yml").write_text(
        "schema: forge/change@2\n"
        "change:\n"
        "  id: CHG-0050\n"
        f"  observable_behavior: {'true' if observable else 'false'}\n",
        encoding="utf-8",
    )
    (change / "specification.md").write_text(specification, encoding="utf-8")
    return change


def test_behavioral_change_requires_a_stable_user_story(tmp_path: Path) -> None:
    _write_change(tmp_path, observable=True, specification="## Classification\n\nBehavior: behavioral\n")

    findings = _validate_all_user_story_contracts(tmp_path)

    assert len(findings) == 1
    assert "at least one stable US-xxx User Story" in findings[0].message


def test_technical_change_without_user_story_is_valid(tmp_path: Path) -> None:
    _write_change(tmp_path, observable=False, specification="## Classification\n\nBehavior: technical\n")

    assert _validate_all_user_story_contracts(tmp_path) == []


def test_story_ids_must_be_unique_and_specification_classification_must_agree(tmp_path: Path) -> None:
    _write_change(
        tmp_path,
        observable=True,
        specification=(
            "## Classification\n\nBehavior: technical\n\n"
            "### US-001 · First\n\n### US-001 · Duplicate\n"
        ),
    )

    messages = [finding.message for finding in _validate_all_user_story_contracts(tmp_path)]

    assert any("does not match" in message for message in messages)
    assert any("duplicate User Story identifier" in message for message in messages)


def test_historical_change_without_semantic_marker_is_preserved(tmp_path: Path) -> None:
    _write_change(tmp_path, observable=False, specification="## User Stories\n\nNo stories.\n")
    manifest = tmp_path / ".forge" / "changes" / "CHG-0050-example" / "manifest.yml"
    manifest.write_text(manifest.read_text(encoding="utf-8").replace("  observable_behavior: false\n", ""), encoding="utf-8")

    assert _validate_all_user_story_contracts(tmp_path) == []


def test_fast_change_without_specification_is_preserved(tmp_path: Path) -> None:
    change = _write_change(tmp_path, observable=True, specification="")
    manifest = change / "manifest.yml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(
            "  observable_behavior: true\n", "  observable_behavior: true\nflow:\n  current: fast\n"
        ),
        encoding="utf-8",
    )
    (change / "specification.md").unlink()

    assert _validate_all_user_story_contracts(tmp_path) == []


def test_indented_code_example_is_not_counted_as_a_user_story(tmp_path: Path) -> None:
    _write_change(
        tmp_path,
        observable=True,
        specification="## Classification\n\nBehavior: behavioral\n\n    ### US-001 · Example\n",
    )

    findings = _validate_all_user_story_contracts(tmp_path)

    assert any("at least one stable US-xxx User Story" in finding.message for finding in findings)


def test_tilde_fenced_code_example_is_not_counted_as_a_user_story(tmp_path: Path) -> None:
    _write_change(
        tmp_path,
        observable=True,
        specification="## Classification\n\nBehavior: behavioral\n\n~~~md\n### US-001 · Example\n~~~\n",
    )

    findings = _validate_all_user_story_contracts(tmp_path)

    assert any("at least one stable US-xxx User Story" in finding.message for finding in findings)


def test_mixed_fence_types_do_not_escape_a_fenced_code_block(tmp_path: Path) -> None:
    _write_change(
        tmp_path,
        observable=True,
        specification="## Classification\n\nBehavior: behavioral\n\n```md\n~~~\n### US-001 · Example\n~~~\n```\n",
    )

    findings = _validate_all_user_story_contracts(tmp_path)

    assert any("at least one stable US-xxx User Story" in finding.message for finding in findings)


def test_fence_info_does_not_close_an_open_fence(tmp_path: Path) -> None:
    _write_change(
        tmp_path,
        observable=True,
        specification="## Classification\n\nBehavior: behavioral\n\n```md\n```python\n### US-001 · Example\n```\n",
    )

    findings = _validate_all_user_story_contracts(tmp_path)

    assert any("at least one stable US-xxx User Story" in finding.message for finding in findings)


def test_fenced_verification_example_is_not_evidence(tmp_path: Path) -> None:
    change = _write_change(
        tmp_path,
        observable=True,
        specification="## Classification\n\nBehavior: behavioral\n\n### US-001 · First\n\n#### Acceptance Criteria\n##### AC-001\n",
    )
    manifest = change / "manifest.yml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace("  observable_behavior: true\n", "  observable_behavior: true\nstate:\n  current: implementation\n"),
        encoding="utf-8",
    )
    (change / "tasks.md").write_text("- [x] T-001 Implement first\n", encoding="utf-8")
    (change / "verification.md").write_text("```md\n| AC-001 | FR-001 | PASS | example |\n```\n", encoding="utf-8")
    (change / "traceability.yml").write_text(
        "schema: forge/traceability@1\nchange: CHG-0050\nrequirements: {}\n"
        "stories:\n  US-001:\n    tasks: [T-001]\n    verification: [AC-001]\n",
        encoding="utf-8",
    )

    findings = _validate_all_user_story_traceability(tmp_path)

    assert any("without passing repository-native evidence" in finding.message for finding in findings)


def test_implementation_requires_each_story_to_have_tasks_and_verification(tmp_path: Path) -> None:
    change = _write_change(
        tmp_path,
        observable=True,
        specification=(
            "## Classification\n\nBehavior: behavioral\n\n"
            "### US-001 · First\n\n### US-002 · Second\n"
        ),
    )
    manifest = change / "manifest.yml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace("  observable_behavior: true\n", "  observable_behavior: true\nstate:\n  current: implementation\n"),
        encoding="utf-8",
    )
    (change / "traceability.yml").write_text(
        "schema: forge/traceability@1\nchange: CHG-0050\nrequirements: {}\n"
        "stories:\n  US-001:\n    tasks: [T-001]\n    verification: [AC-001]\n",
        encoding="utf-8",
    )
    (change / "tasks.md").write_text("- [x] T-001 Implement first\n", encoding="utf-8")
    (change / "verification.md").write_text("| AC-001 | FR-001 | PASS | test |\n", encoding="utf-8")

    messages = [finding.message for finding in _validate_all_user_story_traceability(tmp_path)]

    assert any("US-002" in message and "traceability" in message for message in messages)


def test_story_traceability_rejects_orphan_story_and_missing_verification(tmp_path: Path) -> None:
    change = _write_change(
        tmp_path,
        observable=True,
        specification="## Classification\n\nBehavior: behavioral\n\n### US-001 · First\n",
    )
    manifest = change / "manifest.yml"
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace("  observable_behavior: true\n", "  observable_behavior: true\nstate:\n  current: complete\n"),
        encoding="utf-8",
    )
    (change / "traceability.yml").write_text(
        "schema: forge/traceability@1\nchange: CHG-0050\nrequirements: {}\n"
        "stories:\n  US-001:\n    tasks: [T-001]\n  US-999:\n    tasks: [T-999]\n    verification: [AC-999]\n",
        encoding="utf-8",
    )
    (change / "tasks.md").write_text("- [x] T-001 Implement first\n", encoding="utf-8")
    (change / "verification.md").write_text("| AC-001 | FR-001 | PENDING | test |\n", encoding="utf-8")

    messages = [finding.message for finding in _validate_all_user_story_traceability(tmp_path)]

    assert any("US-001" in message and "Verification" in message for message in messages)
    assert any("US-999" in message and "not present" in message for message in messages)
