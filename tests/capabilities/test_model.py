import dataclasses
from pathlib import Path

import pytest

from forge_cli.capabilities.model import Capability

_EXPECTED_FIELDS = {
    "id",
    "schema",
    "identity",
    "purpose",
    "applicability",
    "inputs",
    "behavior",
    "outputs",
    "evidence_expectations",
    "source_path",
}


def _sample_capability(source_path: Path) -> Capability:
    return Capability(
        id="sample",
        schema=1,
        identity="Sample capability identity.",
        purpose="Sample capability purpose.",
        applicability="Sample capability applicability.",
        inputs="Sample capability inputs.",
        behavior="Sample capability behavior.",
        outputs="Sample capability outputs.",
        evidence_expectations="Sample capability evidence expectations.",
        source_path=source_path,
    )


def test_capability_exposes_exactly_the_minimal_field_set() -> None:
    field_names = {field.name for field in dataclasses.fields(Capability)}

    assert field_names == _EXPECTED_FIELDS


def test_capability_is_frozen(tmp_path: Path) -> None:
    capability = _sample_capability(tmp_path / "CAPABILITY.md")

    with pytest.raises(dataclasses.FrozenInstanceError):
        capability.identity = "mutated"  # type: ignore[misc]


def test_capability_carries_no_harness_specific_field() -> None:
    field_names = {field.name for field in dataclasses.fields(Capability)}

    harness_markers = ("claude", "codex", "cursor")
    assert not any(marker in name for name in field_names for marker in harness_markers)
