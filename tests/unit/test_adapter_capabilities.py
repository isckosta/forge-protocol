from __future__ import annotations

from forge_cli.adapters.capabilities import (
    CapabilityRequirement,
    RequirementSource,
    evaluate_capability_requirements,
)


def test_supported_forge_requirement_produces_no_limitation() -> None:
    requirements = [
        CapabilityRequirement(
            requirement_id="strict-review",
            capability="hooks",
            source=RequirementSource.FORGE,
            source_reference="C-022",
        )
    ]

    limitations = evaluate_capability_requirements(
        declared_capabilities={"hooks": True},
        requirements=requirements,
    )

    assert limitations == ()


def test_unsupported_forge_requirement_is_reported_explicitly() -> None:
    requirements = [
        CapabilityRequirement(
            requirement_id="strict-review",
            capability="hooks",
            source=RequirementSource.FORGE,
            source_reference="C-022",
        )
    ]

    limitations = evaluate_capability_requirements(
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
    requirement = CapabilityRequirement(
        requirement_id="adapter-rendering",
        capability="generated_files",
        source=RequirementSource.ADAPTER_INTERNAL,
        source_reference="adapter:example",
    )

    assert requirement.source is RequirementSource.ADAPTER_INTERNAL


def test_limitation_order_is_deterministic() -> None:
    requirements = [
        CapabilityRequirement("review", "hooks", RequirementSource.FORGE, "C-022"),
        CapabilityRequirement("tdd-red", "commands", RequirementSource.FORGE, "C-009"),
    ]

    limitations = evaluate_capability_requirements(
        declared_capabilities={"hooks": False, "commands": False},
        requirements=requirements,
    )

    assert [item.requirement_id for item in limitations] == ["review", "tdd-red"]
