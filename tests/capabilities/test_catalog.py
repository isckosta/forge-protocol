from pathlib import Path

import pytest

from forge_cli.capabilities.exposure import derive_capability_exposures
from forge_cli.capabilities.loader import load_capability_catalog
from forge_cli.capabilities.model import Capability


def test_catalog_is_deterministic_and_contains_all_canonical_capabilities() -> None:
    root = Path(__file__).resolve().parents[2] / "capabilities"

    catalog = load_capability_catalog(root)

    assert tuple(item.id for item in catalog) == ("fix", "investigate", "qa")
    assert all(item.source_path.name == "CAPABILITY.md" for item in catalog)


def test_forge_workflow_name_is_reserved_for_native_exposure() -> None:
    capability = Capability(
        id="forge",
        schema=1,
        identity="identity",
        purpose="purpose",
        applicability="applicability",
        inputs="inputs",
        behavior="behavior",
        outputs="outputs",
        evidence_expectations="evidence",
        source_path=Path("CAPABILITY.md"),
    )

    with pytest.raises(ValueError, match="Reserved capability invocation id"):
        derive_capability_exposures((capability,))


def test_workflow_reference_namespace_is_reserved_for_native_exposure() -> None:
    capability = Capability(
        id="references",
        schema=1,
        identity="identity",
        purpose="purpose",
        applicability="applicability",
        inputs="inputs",
        behavior="behavior",
        outputs="outputs",
        evidence_expectations="evidence",
        source_path=Path("CAPABILITY.md"),
    )

    with pytest.raises(ValueError, match="Reserved capability invocation id"):
        derive_capability_exposures((capability,))
