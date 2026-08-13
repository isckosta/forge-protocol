from __future__ import annotations

import importlib

import pytest

from forge_cli.adapters.plan import OperationIntent, OwnershipMode, digest_content


def ownership_module():
    try:
        return importlib.import_module("forge_cli.adapters.ownership")
    except ModuleNotFoundError:
        pytest.fail("Adapter ownership classification is not implemented yet")


def test_missing_target_is_classified_as_create() -> None:
    module = ownership_module()

    decision = module.classify_artifact(
        ownership=OwnershipMode.FORGE_OWNED,
        exists=False,
        current_digest=None,
        expected_digest=None,
        merge_result=None,
    )

    assert decision.intent is OperationIntent.CREATE
    assert decision.safe_to_apply is True


def test_existing_user_owned_target_is_preserved() -> None:
    module = ownership_module()

    decision = module.classify_artifact(
        ownership=OwnershipMode.USER_OWNED,
        exists=True,
        current_digest=digest_content("user content"),
        expected_digest=None,
        merge_result=None,
    )

    assert decision.intent is OperationIntent.PRESERVE
    assert decision.safe_to_apply is False


def test_forge_owned_target_may_update_only_when_expected_state_matches() -> None:
    module = ownership_module()
    recorded_digest = digest_content("generated v1")

    decision = module.classify_artifact(
        ownership=OwnershipMode.FORGE_OWNED,
        exists=True,
        current_digest=recorded_digest,
        expected_digest=recorded_digest,
        merge_result=None,
    )

    assert decision.intent is OperationIntent.UPDATE
    assert decision.safe_to_apply is True


def test_recorded_equal_desired_file_is_unchanged() -> None:
    module = ownership_module()

    try:
        decision = module.classify_artifact(
            ownership=OwnershipMode.FORGE_OWNED,
            exists=True,
            current_digest=digest_content("same"),
            expected_digest=digest_content("same"),
            desired_digest=digest_content("same"),
            merge_result=None,
        )
    except TypeError as exc:
        pytest.fail(f"Recorded desired state is not accepted: {exc}")

    assert decision.intent.value == "unchanged"
    assert decision.safe_to_apply is True


def test_unrecorded_equal_desired_file_conflicts_without_silent_adoption() -> None:
    module = ownership_module()

    decision = module.classify_artifact(
        ownership=OwnershipMode.FORGE_OWNED,
        exists=True,
        current_digest=digest_content("same"),
        expected_digest=None,
        desired_digest=digest_content("same"),
        merge_result=None,
    )

    assert decision.intent is OperationIntent.CONFLICT
    assert decision.safe_to_apply is False


def test_forge_owned_target_without_proven_expected_state_conflicts() -> None:
    module = ownership_module()

    decision = module.classify_artifact(
        ownership=OwnershipMode.FORGE_OWNED,
        exists=True,
        current_digest=digest_content("unknown state"),
        expected_digest=None,
        merge_result=None,
    )

    assert decision.intent is OperationIntent.CONFLICT
    assert decision.safe_to_apply is False


def test_forge_owned_target_with_mismatched_state_conflicts() -> None:
    module = ownership_module()

    decision = module.classify_artifact(
        ownership=OwnershipMode.FORGE_OWNED,
        exists=True,
        current_digest=digest_content("modified outside forge"),
        expected_digest=digest_content("generated v1"),
        merge_result=None,
    )

    assert decision.intent is OperationIntent.CONFLICT
    assert decision.safe_to_apply is False


def test_shared_target_without_explicit_merge_result_conflicts() -> None:
    module = ownership_module()

    decision = module.classify_artifact(
        ownership=OwnershipMode.SHARED,
        exists=True,
        current_digest=digest_content("shared content"),
        expected_digest=None,
        merge_result=None,
    )

    assert decision.intent is OperationIntent.CONFLICT
    assert decision.safe_to_apply is False


def test_shared_target_with_explicit_merge_result_may_update() -> None:
    module = ownership_module()

    decision = module.classify_artifact(
        ownership=OwnershipMode.SHARED,
        exists=True,
        current_digest=digest_content("shared content"),
        expected_digest=None,
        merge_result="deterministically merged content",
    )

    assert decision.intent is OperationIntent.UPDATE
    assert decision.safe_to_apply is True
    assert decision.content == "deterministically merged content"
