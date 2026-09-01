"""Proves capabilities/investigate/CAPABILITY.md satisfies the existing
Capability contract and loads through the existing, unmodified loader
(CHG-0052 TD-001-TD-006).

These tests deliberately avoid freezing full prose: they check for the
literal conclusion/evidence markers the original request requires
verbatim, and for key-term presence elsewhere, not for exact sentences.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from forge_cli.capabilities.loader import load_capability
from forge_cli.capabilities.model import Capability

_CAPABILITY_PATH = Path(__file__).resolve().parents[2] / "capabilities" / "investigate" / "CAPABILITY.md"

_FORBIDDEN_TERMS = (
    "claude",
    "codex",
    "cursor",
    "capabilityregistry",
    "capabilityexecutor",
    "/investigate",
    "skill.md",
)

_BOUNDARY_DENIAL_FRAGMENTS = (
    "approv",  # covers "approve"/"approval"
    "flow",
    "gate",
    "lifecycle",
    "decis",  # covers "decision"/"decisions"
)

_SEQUENCE_KEY_TERMS = (
    "hypothes",
    "reproduc",
    "evidence",
    "root cause",
)


@pytest.fixture(scope="module")
def capability() -> Capability:
    return load_capability(_CAPABILITY_PATH)


@pytest.fixture(scope="module")
def raw_text() -> str:
    return _CAPABILITY_PATH.read_text(encoding="utf-8")


def test_investigate_capability_loads_via_existing_loader(capability: Capability) -> None:
    assert capability.id == "investigate"
    assert isinstance(capability.schema, int)
    for section in (
        capability.identity,
        capability.purpose,
        capability.applicability,
        capability.inputs,
        capability.behavior,
        capability.outputs,
        capability.evidence_expectations,
    ):
        assert section.strip()


def test_root_cause_conclusion_markers_are_literal(capability: Capability) -> None:
    combined = capability.behavior + "\n" + capability.outputs
    assert "ROOT CAUSE CONFIRMED" in combined
    assert "ROOT CAUSE NOT ESTABLISHED" in combined


def test_evidence_classification_is_declared(capability: Capability) -> None:
    assert "CONFIRMED" in capability.evidence_expectations
    assert "INFERRED" in capability.evidence_expectations
    assert "UNKNOWN" in capability.evidence_expectations


@pytest.mark.parametrize("forbidden_term", _FORBIDDEN_TERMS)
def test_no_harness_or_forbidden_mechanism_vocabulary(raw_text: str, forbidden_term: str) -> None:
    assert forbidden_term not in raw_text.lower()


@pytest.mark.parametrize("fragment", _BOUNDARY_DENIAL_FRAGMENTS)
def test_boundary_denial_fragments_are_present(raw_text: str, fragment: str) -> None:
    assert fragment in raw_text.lower()


@pytest.mark.parametrize("term", _SEQUENCE_KEY_TERMS)
def test_evidence_driven_sequence_key_terms_are_named(capability: Capability, term: str) -> None:
    assert term in capability.behavior.lower()


def test_plausible_guess_antipattern_is_named(capability: Capability) -> None:
    assert "plausible guess" in capability.behavior.lower()
