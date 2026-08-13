from __future__ import annotations

import importlib

import pytest


def capabilities_module():
    try:
        return importlib.import_module("forge_cli.adapters.capabilities")
    except ModuleNotFoundError:
        pytest.fail("Adapter capability model is not implemented yet")


def test_supported_forge_requirement_produces_no_limitation() -> None:
    module = capabilities_module()
    requirements = [
        module.CapabilityRequirement(
            requirement_id="strict-review",
            capability="hooks",
            source=module.RequirementSource.FORGE,
            source_reference="C-022",
        )
    ]

    limitations = module.evaluate_capability_requirements(
        declared_capabilities={"hooks": True},
        requirements=requirements,
    )

    assert limitations == ()


def test_unsupported_forge_requirement_is_reported_explicitly() -> None:
    module = capabilities_module()
    requirements = [
        module.CapabilityRequirement(
            requirement_id="strict-review",
            capability="hooks",
            source=module.RequirementSource.FORGE,
            source_reference="C-022",
        )
    ]

    limitations = module.evaluate_capability_requirements(
        declared_capabilities={"hooks": False},
        requirements=requirements,
    )

    assert len(limitations) == 1
    limitation = limitations[0]
    assert limitation.requirement_id == "strict-review"
    assert limitation.capability == "hooks"
    assert limitation.source_reference == "C-022"
    assert limitation.enforced is False


def test_adapter_internal_requirement_is_distinct_from_forge_requirement() -> None:
    module = capabilities_module()
    requirement = module.CapabilityRequirement(
        requirement_id="adapter-rendering",
        capability="generated_files",
        source=module.RequirementSource.ADAPTER_INTERNAL,
        source_reference="adapter:example",
    )

    assert requirement.source is module.RequirementSource.ADAPTER_INTERNAL


def test_limitation_order_is_deterministic() -> None:
    module = capabilities_module()
    requirements = [
        module.CapabilityRequirement("review", "hooks", module.RequirementSource.FORGE, "C-022"),
        module.CapabilityRequirement("tdd-red", "commands", module.RequirementSource.FORGE, "C-009"),
    ]

    limitations = module.evaluate_capability_requirements(
        declared_capabilities={"hooks": False, "commands": False},
        requirements=requirements,
    )

    assert [item.requirement_id for item in limitations] == ["review", "tdd-red"]
