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


def test_passed_status_with_stopped_phase_is_flagged() -> None:
    """Codex PR #44 review (P2): the reverse direction was previously
    unchecked -- a manifest could claim review.status: passed while
    current_phase: stopped (or any other non-converged phase), silently
    contradicting the phase's own non-completion signal (FR-007)."""
    manifest = {
        "review": {"status": "passed", "current_phase": "stopped", "iterations": [{"id": "review-001"}]},
    }

    findings = validation._validate_review_current_phase(manifest)

    assert len(findings) == 1
    assert "stopped" in findings[0].message


def test_passed_status_with_findings_recorded_phase_is_flagged() -> None:
    """Codex PR #44 review (P2), reverse direction, a second non-converged phase."""
    manifest = {
        "review": {"status": "passed", "current_phase": "findings_recorded", "iterations": [{"id": "review-001"}]},
    }

    findings = validation._validate_review_current_phase(manifest)

    assert len(findings) == 1
