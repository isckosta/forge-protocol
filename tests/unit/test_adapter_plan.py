from __future__ import annotations

import importlib

import pytest


def plan_module():
    try:
        return importlib.import_module("forge_cli.adapters.plan")
    except ModuleNotFoundError:
        pytest.fail("Adapter plan model is not implemented yet")


def test_ownership_and_intent_vocabularies_are_canonical() -> None:
    module = plan_module()

    assert {item.value for item in module.OwnershipMode} == {
        "forge_owned",
        "user_owned",
        "shared",
    }
    assert {item.value for item in module.OperationIntent} == {
        "create",
        "update",
        "unchanged",
        "preserve",
        "conflict",
        "delete_generated",
    }


def test_operation_from_content_has_deterministic_digest_and_is_immutable() -> None:
    module = plan_module()

    operation = module.AdapterOperation.from_content(
        path=".cursor/rules/forge.md",
        ownership=module.OwnershipMode.FORGE_OWNED,
        intent=module.OperationIntent.CREATE,
        content="Forge rules\n",
    )

    assert operation.content_digest == module.digest_content("Forge rules\n")
    with pytest.raises(AttributeError):
        operation.path = "changed"


def test_plan_operations_are_stably_ordered() -> None:
    module = plan_module()
    later = module.AdapterOperation.from_content(
        path="z/rules.md",
        ownership=module.OwnershipMode.FORGE_OWNED,
        intent=module.OperationIntent.CREATE,
        content="z",
    )
    earlier = module.AdapterOperation.from_content(
        path="a/rules.md",
        ownership=module.OwnershipMode.SHARED,
        intent=module.OperationIntent.PRESERVE,
        content="a",
    )

    plan = module.AdapterPlan(adapter_id="example", operations=[later, earlier])

    assert [operation.path for operation in plan.operations] == ["a/rules.md", "z/rules.md"]


def test_plan_carries_limitations_and_conflicts_as_immutable_collections() -> None:
    module = plan_module()

    plan = module.AdapterPlan(
        adapter_id="example",
        operations=[],
        limitations=["strict-review-not-enforced"],
        conflicts=[".cursor/rules/forge.md"],
    )

    assert plan.limitations == ("strict-review-not-enforced",)
    assert plan.conflicts == (".cursor/rules/forge.md",)
