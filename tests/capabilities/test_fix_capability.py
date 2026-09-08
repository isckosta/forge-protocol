"""Proves the canonical ``fix`` Capability satisfies the existing contract."""

from __future__ import annotations

from pathlib import Path

import pytest

from forge_cli.capabilities.loader import load_capability
from forge_cli.capabilities.model import Capability

_CAPABILITY_PATH = Path(__file__).resolve().parents[2] / "capabilities" / "fix" / "CAPABILITY.md"

_FORBIDDEN_TERMS = ("claude", "codex", "cursor", "skill.md", "fix.md")
_REQUIRED_INPUTS = ("bug", "failing test", "stack trace", "investigate")
_BOUNDARY_TERMS = ("flow", "gate", "approval", "merge", "breaking change", "architecture")


@pytest.fixture(scope="module")
def capability() -> Capability:
    return load_capability(_CAPABILITY_PATH)


@pytest.fixture(scope="module")
def raw_text() -> str:
    return _CAPABILITY_PATH.read_text(encoding="utf-8").lower()


def test_fix_capability_loads_via_existing_loader(capability: Capability) -> None:
    assert capability.id == "fix"
    assert isinstance(capability.schema, int)
    assert all(
        section.strip()
        for section in (
            capability.identity,
            capability.purpose,
            capability.applicability,
            capability.inputs,
            capability.behavior,
            capability.outputs,
            capability.evidence_expectations,
        )
    )


@pytest.mark.parametrize("term", _REQUIRED_INPUTS)
def test_accepts_supported_problem_inputs(capability: Capability, term: str) -> None:
    assert term in (capability.inputs + "\n" + capability.applicability).lower()


@pytest.mark.parametrize("term", ("observed", "expected", "cause", "boundary"))
def test_requires_sufficient_understanding(capability: Capability, term: str) -> None:
    assert term in capability.behavior.lower()


def test_declares_escalation_when_understanding_is_insufficient(capability: Capability) -> None:
    text = capability.behavior.lower() + "\n" + capability.outputs.lower()
    assert "investigat" in text
    assert "not" in text
    assert "cause" in text


@pytest.mark.parametrize("term", ("smallest", "minimal", "root cause", "symptom"))
def test_preserves_minimal_cause_oriented_scope(capability: Capability, term: str) -> None:
    text = capability.purpose + "\n" + capability.behavior
    assert term in text.lower()


@pytest.mark.parametrize("term", _BOUNDARY_TERMS)
def test_detects_material_scope_expansion(raw_text: str, term: str) -> None:
    assert term in raw_text


def test_declares_reproducible_regression_evidence(capability: Capability) -> None:
    text = capability.outputs + "\n" + capability.evidence_expectations
    for term in ("regression", "reproduc", "test", "evidence"):
        assert term in text.lower()


@pytest.mark.parametrize("forbidden", _FORBIDDEN_TERMS)
def test_has_no_harness_or_new_artifact_coupling(raw_text: str, forbidden: str) -> None:
    assert forbidden not in raw_text


def test_does_not_redefine_forge_governance(raw_text: str) -> None:
    for term in ("redefine", "flow", "gate", "approval", "merge readiness"):
        assert term in raw_text
