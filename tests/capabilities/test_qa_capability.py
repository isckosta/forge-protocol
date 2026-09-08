"""Proves the canonical ``qa`` Capability satisfies the existing contract."""

from __future__ import annotations

from pathlib import Path

import pytest

from forge_cli.capabilities.loader import load_capability
from forge_cli.capabilities.model import Capability

_CAPABILITY_PATH = Path(__file__).resolve().parents[2] / "capabilities" / "qa" / "CAPABILITY.md"

_FORBIDDEN_HARNESS_OR_MECHANISM_TERMS = (
    "claude",
    "codex",
    "cursor",
    "skill.md",
    "capabilityregistry",
    "capabilityexecutor",
)


@pytest.fixture(scope="module")
def capability() -> Capability:
    return load_capability(_CAPABILITY_PATH)


@pytest.fixture(scope="module")
def raw_text() -> str:
    return _CAPABILITY_PATH.read_text(encoding="utf-8").lower()


def test_qa_capability_loads_via_existing_loader(capability: Capability) -> None:
    assert capability.id == "qa"
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


@pytest.mark.parametrize(
    "term",
    ("happy path", "edge case", "invalid", "error", "combination", "boundary"),
)
def test_exploration_scope_is_explicit(capability: Capability, term: str) -> None:
    assert term in capability.behavior.lower()


@pytest.mark.parametrize(
    "term",
    ("observed behavior", "expected behavior", "reproduction", "evidence", "impact"),
)
def test_findings_have_reproducible_observable_shape(capability: Capability, term: str) -> None:
    text = capability.outputs.lower() + "\n" + capability.evidence_expectations.lower()
    assert term in text


@pytest.mark.parametrize(
    "term",
    ("verification", "review", "investigate", "fix"),
)
def test_distinguishes_adjacent_competencies(capability: Capability, term: str) -> None:
    assert term in capability.applicability.lower() + "\n" + capability.behavior.lower()


@pytest.mark.parametrize(
    "term",
    ("root cause", "assum", "correct", "requirement"),
)
def test_preserves_observation_over_inference_boundary(capability: Capability, term: str) -> None:
    text = capability.behavior.lower() + "\n" + capability.outputs.lower()
    assert term in text


@pytest.mark.parametrize(
    "term",
    ("gate", "flow", "lifecycle", "artifact", "executor", "registry", "enforcement"),
)
def test_declares_governance_and_mechanism_boundaries(raw_text: str, term: str) -> None:
    assert term in raw_text


@pytest.mark.parametrize("forbidden", _FORBIDDEN_HARNESS_OR_MECHANISM_TERMS)
def test_is_harness_independent_and_not_a_harness_projection(raw_text: str, forbidden: str) -> None:
    assert forbidden not in raw_text


def test_does_not_claim_to_fix_or_establish_cause(capability: Capability) -> None:
    text = capability.behavior.lower() + "\n" + capability.outputs.lower()
    assert "must not fix" in text
    assert "root cause" in text
