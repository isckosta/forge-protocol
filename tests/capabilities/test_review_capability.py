"""Proves the canonical ``review`` Capability satisfies its contract."""

from pathlib import Path

import pytest

from forge_cli.capabilities.loader import load_capability
from forge_cli.capabilities.model import Capability

_CAPABILITY_PATH = Path(__file__).resolve().parents[2] / "capabilities" / "review" / "CAPABILITY.md"

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


def test_review_capability_loads_via_existing_loader(capability: Capability) -> None:
    assert capability.id == "review"
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
    ("obligation", "effective review profile", "defect", "regression", "inconsistency", "risk", "unsupported claim"),
)
def test_review_is_critical_and_adversarial(capability: Capability, term: str) -> None:
    assert term in capability.inputs.lower() + "\n" + capability.behavior.lower()


@pytest.mark.parametrize(
    "term",
    ("location", "observed", "expected", "impact", "severity", "materiality", "evidence gap"),
)
def test_findings_are_clear_and_evidence_bearing(capability: Capability, term: str) -> None:
    text = capability.outputs.lower() + "\n" + capability.evidence_expectations.lower()
    assert term in text


@pytest.mark.parametrize(
    "term",
    ("flow", "gate", "approval", "completion", "independence", "provenance", "human authority", "lifecycle", "executor", "registry", "orchestration"),
)
def test_governance_remains_outside_review(raw_text: str, term: str) -> None:
    assert term in raw_text


@pytest.mark.parametrize("forbidden", _FORBIDDEN_HARNESS_OR_MECHANISM_TERMS)
def test_is_harness_independent_and_not_a_harness_projection(raw_text: str, forbidden: str) -> None:
    assert forbidden not in raw_text


def test_review_does_not_select_or_modify_the_effective_profile(raw_text: str) -> None:
    assert "does not select" in raw_text
    assert "does not modify" in raw_text
