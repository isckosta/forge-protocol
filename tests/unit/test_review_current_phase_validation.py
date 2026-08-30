from forge_cli import validation


def test_converged_phase_with_passed_status_has_no_finding() -> None:
    """CHG-0050 TDD-006 (FR-004, AC-010)."""
    manifest = {
        "review": {"status": "passed", "current_phase": "converged", "iterations": [{"id": "review-001"}]},
    }

    assert validation._validate_review_current_phase(manifest) == []


def test_absent_phase_with_no_iterations_has_no_finding() -> None:
    """CHG-0050 TDD-006 (FR-004, AC-012b)."""
    manifest = {"review": {"status": "pending", "iterations": []}}

    assert validation._validate_review_current_phase(manifest) == []


def test_converged_phase_with_non_passed_status_is_flagged() -> None:
    """CHG-0050 TDD-007 (FR-004, AC-011)."""
    manifest = {
        "review": {"status": "failed", "current_phase": "converged", "iterations": [{"id": "review-001"}]},
    }

    findings = validation._validate_review_current_phase(manifest)

    assert len(findings) == 1
    assert "converged" in findings[0].message
