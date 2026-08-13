from __future__ import annotations

from forge_cli.adapters.codex.integration import plan_codex_projection
from forge_cli.adapters.codex.projection import (
    CodexProjectionInput,
    generate_codex_projection_bundle,
)
from forge_cli.adapters.codex.targets import resolve_publication_target
from forge_cli.adapters.plan import OwnershipMode


def _canonical() -> CodexProjectionInput:
    return CodexProjectionInput(
        flow_id="full",
        flow_content="stages:\n  - id: verification\n  - id: strict_review\n",
        contract_content="authority: repository-native-forge\n",
    )


def _plan(bundle, root: str):
    target = resolve_publication_target(explicit_target=root)
    assert target is not None
    return plan_codex_projection(
        bundle=bundle,
        target=target,
        project_protocol=1,
        capability_requirements=(),
        repository_state=(),
    )


def test_canonical_input_survives_projection_generation_and_discard() -> None:
    canonical = _canonical()
    before = (
        canonical.flow_id,
        canonical.flow_content,
        canonical.contract_content,
    )

    bundle = generate_codex_projection_bundle(canonical)
    assert bundle.resources
    del bundle

    assert (
        canonical.flow_id,
        canonical.flow_content,
        canonical.contract_content,
    ) == before
    assert "repository-native-forge" in canonical.contract_content


def test_codex_projection_never_requests_shared_ownership() -> None:
    plan = _plan(generate_codex_projection_bundle(_canonical()), "tools/codex")

    assert plan.operations
    assert all(operation.ownership is OwnershipMode.FORGE_OWNED for operation in plan.operations)
    assert all(operation.ownership is not OwnershipMode.SHARED for operation in plan.operations)


def test_publication_convention_cannot_change_canonical_semantics() -> None:
    bundle = generate_codex_projection_bundle(_canonical())
    first = _plan(bundle, "tools/codex-a")
    second = _plan(bundle, "tools/codex-b")

    assert [operation.content_digest for operation in first.operations] == [
        operation.content_digest for operation in second.operations
    ]
    assert [operation.content for operation in first.operations] == [
        operation.content for operation in second.operations
    ]
    assert [operation.path for operation in first.operations] != [
        operation.path for operation in second.operations
    ]


def test_repeated_projection_is_release_stable_without_live_vendor_input() -> None:
    canonical = _canonical()
    first = generate_codex_projection_bundle(canonical)
    second = generate_codex_projection_bundle(canonical)

    assert first == second
