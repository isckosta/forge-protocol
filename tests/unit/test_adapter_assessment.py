from __future__ import annotations

import pytest

try:
    from forge_cli.adapters.assessment import (
        InvariantAssessment,
        InvariantSupport,
        assess_invariant,
        to_generic_limitation,
    )
except ImportError:
    InvariantAssessment = None
    InvariantSupport = None
    assess_invariant = None
    to_generic_limitation = None


def _require_behavior() -> None:
    assert InvariantAssessment is not None, "Invariant assessment is not implemented yet"
    assert InvariantSupport is not None, "Invariant support classification is not implemented yet"
    assert assess_invariant is not None, "Invariant assessment behavior is not implemented yet"
    assert to_generic_limitation is not None, "Generic limitation conversion is not implemented yet"


def test_skill_representation_without_technical_mechanism_is_represented() -> None:
    _require_behavior()
    result = assess_invariant(
        invariant_id="strict-review",
        source_reference="C-022",
        represented=True,
        technical_enforcement=False,
    )
    assert result.support is InvariantSupport.REPRESENTED


def test_proven_technical_mechanism_can_be_enforced() -> None:
    _require_behavior()
    result = assess_invariant(
        invariant_id="generated-artifact-drift",
        source_reference="FR-032",
        represented=True,
        technical_enforcement=True,
    )
    assert result.support is InvariantSupport.ENFORCED


def test_missing_representation_is_unsupported_even_if_enforcement_flag_is_true() -> None:
    _require_behavior()
    result = assess_invariant(
        invariant_id="unknown-invariant",
        source_reference="INV-X",
        represented=False,
        technical_enforcement=True,
    )
    assert result.support is InvariantSupport.UNSUPPORTED


def test_non_enforced_assessment_reuses_generic_limitation_model() -> None:
    _require_behavior()
    assessment = assess_invariant(
        invariant_id="strict-review",
        source_reference="C-022",
        represented=True,
        technical_enforcement=False,
    )
    limitation = to_generic_limitation(assessment, capability="skills")
    assert limitation.requirement_id == "strict-review"
    assert limitation.capability == "skills"
    assert limitation.source_reference == "C-022"
    assert limitation.enforced is False


def test_enforced_assessment_does_not_emit_limitation() -> None:
    _require_behavior()
    assessment = assess_invariant(
        invariant_id="generated-artifact-drift",
        source_reference="FR-032",
        represented=True,
        technical_enforcement=True,
    )
    assert to_generic_limitation(assessment, capability="generated_files") is None
