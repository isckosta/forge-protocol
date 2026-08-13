import pytest

from forge_cli.adapters.capabilities import CapabilityRequirement, RequirementSource
from forge_cli.adapters.manifest import AdapterManifest, IncompatibleAdapterProtocolError
from forge_cli.adapters.plan import OperationIntent, OwnershipMode, digest_content


def _manifest(*, hooks: bool = True) -> AdapterManifest:
    return AdapterManifest(
        adapter_id="example",
        version="1.0.0",
        harness="example-harness",
        protocol_min=1,
        protocol_max_exclusive=2,
        capabilities={
            "persistent_instructions": True,
            "commands": True,
            "skills": True,
            "hooks": hooks,
            "agent_roles": False,
            "generated_files": True,
        },
    )


def test_planner_rejects_incompatible_protocol_before_producing_plan() -> None:
    from forge_cli.adapters import planner

    config = planner.EffectiveAdapterConfiguration(
        project_protocol=2,
        capability_requirements=(),
    )

    with pytest.raises(IncompatibleAdapterProtocolError):
        planner.plan_adapter(
            manifest=_manifest(),
            effective_configuration=config,
            projections=(),
            repository_state=(),
        )


def test_planner_surfaces_capability_limitations_from_effective_configuration() -> None:
    from forge_cli.adapters import planner

    config = planner.EffectiveAdapterConfiguration(
        project_protocol=1,
        capability_requirements=(
            CapabilityRequirement(
                requirement_id="C-022",
                capability="hooks",
                source=RequirementSource.FORGE,
                source_reference="C-022",
            ),
        ),
    )

    plan = planner.plan_adapter(
        manifest=_manifest(hooks=False),
        effective_configuration=config,
        projections=(),
        repository_state=(),
    )

    assert len(plan.limitations) == 1
    assert "C-022" in plan.limitations[0]


def test_planner_classifies_repository_state_without_mutating_it() -> None:
    from forge_cli.adapters import planner

    user_state = planner.RepositoryArtifactState(
        path=".tool/user.md",
        exists=True,
        current_digest=digest_content("user content"),
        expected_digest=None,
    )
    forge_state = planner.RepositoryArtifactState(
        path=".tool/generated.md",
        exists=True,
        current_digest=digest_content("old generated"),
        expected_digest=digest_content("old generated"),
    )
    projections = (
        planner.ProjectedArtifact(
            path=".tool/user.md",
            ownership=OwnershipMode.USER_OWNED,
            content="new generated suggestion",
        ),
        planner.ProjectedArtifact(
            path=".tool/generated.md",
            ownership=OwnershipMode.FORGE_OWNED,
            content="new generated",
        ),
    )

    plan = planner.plan_adapter(
        manifest=_manifest(),
        effective_configuration=planner.EffectiveAdapterConfiguration(1, ()),
        projections=projections,
        repository_state=(user_state, forge_state),
    )

    by_path = {operation.path: operation for operation in plan.operations}
    assert by_path[".tool/user.md"].intent is OperationIntent.PRESERVE
    assert by_path[".tool/generated.md"].intent is OperationIntent.UPDATE
    assert user_state.current_digest == digest_content("user content")
    assert forge_state.current_digest == digest_content("old generated")


def test_shared_projection_requires_named_deterministic_merge_provenance() -> None:
    from forge_cli.adapters import planner

    state = planner.RepositoryArtifactState(
        path=".tool/shared.json",
        exists=True,
        current_digest=digest_content("existing"),
        expected_digest=None,
    )
    without_strategy = planner.ProjectedArtifact(
        path=".tool/shared.json",
        ownership=OwnershipMode.SHARED,
        content="adapter contribution",
        merge_result="merged",
    )

    conflict_plan = planner.plan_adapter(
        manifest=_manifest(),
        effective_configuration=planner.EffectiveAdapterConfiguration(1, ()),
        projections=(without_strategy,),
        repository_state=(state,),
    )

    assert conflict_plan.operations[0].intent is OperationIntent.CONFLICT
    assert conflict_plan.conflicts

    with_strategy = planner.ProjectedArtifact(
        path=".tool/shared.json",
        ownership=OwnershipMode.SHARED,
        content="adapter contribution",
        merge_result="merged",
        merge_strategy_id="json-merge-v1",
    )
    update_plan = planner.plan_adapter(
        manifest=_manifest(),
        effective_configuration=planner.EffectiveAdapterConfiguration(1, ()),
        projections=(with_strategy,),
        repository_state=(state,),
    )

    assert update_plan.operations[0].intent is OperationIntent.UPDATE
    assert update_plan.operations[0].content == "merged"
    assert update_plan.conflicts == ()


def test_repeated_planning_with_identical_inputs_is_semantically_identical() -> None:
    from forge_cli.adapters import planner

    projections = (
        planner.ProjectedArtifact(
            path="z.md",
            ownership=OwnershipMode.FORGE_OWNED,
            content="z",
        ),
        planner.ProjectedArtifact(
            path="a.md",
            ownership=OwnershipMode.FORGE_OWNED,
            content="a",
        ),
    )
    config = planner.EffectiveAdapterConfiguration(1, ())

    first = planner.plan_adapter(
        manifest=_manifest(),
        effective_configuration=config,
        projections=projections,
        repository_state=(),
    )
    second = planner.plan_adapter(
        manifest=_manifest(),
        effective_configuration=config,
        projections=reversed(projections),
        repository_state=(),
    )

    assert first == second
    assert [operation.path for operation in first.operations] == ["a.md", "z.md"]
