import importlib
from pathlib import Path

import pytest

from forge_cli.adapters.manifest import AdapterManifest
from forge_cli.adapters.plan import AdapterPlan, OperationIntent, OwnershipMode, digest_content
from forge_cli.adapters.planner import (
    EffectiveAdapterConfiguration,
    ProjectedArtifact,
    RepositoryArtifactState,
    plan_adapter,
)
from forge_cli.adapters.state import (
    AdapterInstallationRecord,
    GeneratedArtifact,
    write_installation_record,
)


def publisher_module():
    try:
        return importlib.import_module("forge_cli.adapters.publisher")
    except ModuleNotFoundError:
        pytest.fail("Safe Adapter publisher is not implemented yet")


def _manifest() -> AdapterManifest:
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
            "hooks": True,
            "agent_roles": True,
            "generated_files": True,
        },
    )


def _record(
    *artifacts: tuple[str, str],
    adapter_id: str = "example",
    publication_root: str = ".",
) -> AdapterInstallationRecord:
    return AdapterInstallationRecord(
        adapter_id=adapter_id,
        adapter_version="1.0.0",
        harness="example-harness",
        protocol_min=1,
        protocol_max_exclusive=2,
        publication_root=publication_root,
        generated_artifacts=(GeneratedArtifact(path=path, digest=digest) for path, digest in artifacts),
        limitations=(),
    )


def _write_prior_record(
    root: Path,
    *artifacts: tuple[str, str],
    publication_root: str = ".",
) -> None:
    write_installation_record(
        root / ".forge/adapters/example/installation.yml",
        _record(*artifacts, publication_root=publication_root),
    )


def test_conflicted_plan_is_refused_before_any_mutation(tmp_path: Path) -> None:
    publisher = publisher_module()
    target = tmp_path / "user.md"
    target.write_text("user", encoding="utf-8")
    plan = AdapterPlan(adapter_id="example", operations=(), conflicts=("user.md: collision",))

    with pytest.raises(publisher.AdapterPublicationConflictError):
        publisher.publish_adapter_plan(tmp_path, plan, _record())

    assert target.read_text(encoding="utf-8") == "user"
    assert not (tmp_path / ".forge/adapters/example/installation.yml").exists()


def test_user_owned_preserve_operation_never_overwrites_existing_content(tmp_path: Path) -> None:
    publisher = publisher_module()
    target = tmp_path / "user.md"
    target.write_text("user", encoding="utf-8")
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(ProjectedArtifact(path="user.md", ownership=OwnershipMode.USER_OWNED, content="adapter"),),
        repository_state=(RepositoryArtifactState(path="user.md", exists=True, current_digest=digest_content("user"), expected_digest=None),),
    )

    publisher.publish_adapter_plan(tmp_path, plan, _record())

    assert target.read_text(encoding="utf-8") == "user"


def test_forge_owned_update_revalidates_planning_precondition_before_write(tmp_path: Path) -> None:
    target = tmp_path / "generated.md"
    target.write_text("old", encoding="utf-8")
    _write_prior_record(tmp_path, ("generated.md", digest_content("old")))
    installation_path = tmp_path / ".forge/adapters/example/installation.yml"
    installation_before = installation_path.read_bytes()
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(ProjectedArtifact(path="generated.md", ownership=OwnershipMode.FORGE_OWNED, content="new"),),
        repository_state=(RepositoryArtifactState(path="generated.md", exists=True, current_digest=digest_content("old"), expected_digest=digest_content("old")),),
    )

    assert hasattr(plan.operations[0], "expected_current_digest"), "Adapter operation publication precondition is not implemented yet"
    assert plan.operations[0].expected_current_digest == digest_content("old")

    publisher = publisher_module()
    target.write_text("changed-after-plan", encoding="utf-8")

    with pytest.raises(publisher.AdapterPublicationConflictError):
        publisher.publish_adapter_plan(tmp_path, plan, _record(("generated.md", digest_content("new"))))

    assert target.read_text(encoding="utf-8") == "changed-after-plan"
    assert installation_path.read_bytes() == installation_before


def test_create_publishes_content_and_installation_record_last(tmp_path: Path) -> None:
    publisher = publisher_module()
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(ProjectedArtifact(path="generated.md", ownership=OwnershipMode.FORGE_OWNED, content="new"),),
        repository_state=(),
    )

    publisher.publish_adapter_plan(tmp_path, plan, _record(("generated.md", digest_content("new"))))

    assert (tmp_path / "generated.md").read_text(encoding="utf-8") == "new"
    assert (tmp_path / ".forge/adapters/example/installation.yml").exists()


def test_create_revalidates_absence_immediately_before_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    publisher = publisher_module()
    target = tmp_path / "generated.md"
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(ProjectedArtifact(path="generated.md", ownership=OwnershipMode.FORGE_OWNED, content="new"),),
        repository_state=(),
    )
    original_record_validation = publisher._validate_record_matches_plan

    def create_external_file_after_preflight(plan, record) -> None:
        original_record_validation(plan, record)
        target.write_text("external", encoding="utf-8")

    monkeypatch.setattr(publisher, "_validate_record_matches_plan", create_external_file_after_preflight)

    with pytest.raises(publisher.AdapterPublicationConflictError):
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(("generated.md", digest_content("new"))),
        )

    assert target.read_text(encoding="utf-8") == "external"
    assert not (tmp_path / ".forge/adapters/example/installation.yml").exists()


def test_repository_escape_path_is_rejected_without_writing_outside_root(tmp_path: Path) -> None:
    publisher = publisher_module()
    outside = tmp_path.parent / "forge-outside.txt"
    if outside.exists():
        outside.unlink()
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(ProjectedArtifact(path="../forge-outside.txt", ownership=OwnershipMode.FORGE_OWNED, content="escape"),),
        repository_state=(),
    )

    with pytest.raises(publisher.UnsafeAdapterPathError):
        publisher.publish_adapter_plan(tmp_path, plan, _record())

    assert not outside.exists()


def test_backslash_path_is_rejected_as_cross_platform_ambiguous(tmp_path: Path) -> None:
    publisher = publisher_module()
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(ProjectedArtifact(path=r"tool\generated.md", ownership=OwnershipMode.FORGE_OWNED, content="ambiguous"),),
        repository_state=(),
    )

    with pytest.raises(publisher.UnsafeAdapterPathError):
        publisher.publish_adapter_plan(tmp_path, plan, _record())

    assert not (tmp_path / r"tool\generated.md").exists()


def test_symlink_escape_is_rejected(tmp_path: Path) -> None:
    publisher = publisher_module()
    outside = tmp_path.parent / "forge-outside-dir"
    outside.mkdir(exist_ok=True)
    link = tmp_path / "tool"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlinks are unavailable in this environment")

    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(ProjectedArtifact(path="tool/generated.md", ownership=OwnershipMode.FORGE_OWNED, content="escape"),),
        repository_state=(),
    )

    with pytest.raises(publisher.UnsafeAdapterPathError):
        publisher.publish_adapter_plan(tmp_path, plan, _record())

    assert not (outside / "generated.md").exists()


def test_adapter_id_cannot_escape_installation_state_directory(tmp_path: Path) -> None:
    publisher = publisher_module()
    plan = AdapterPlan(adapter_id="../escape", operations=())

    with pytest.raises(publisher.UnsafeAdapterPathError):
        publisher.publish_adapter_plan(tmp_path, plan, _record(adapter_id="../escape"))

    assert not (tmp_path / ".forge/escape/installation.yml").exists()


def test_installation_record_digest_must_match_planned_forge_owned_content(tmp_path: Path) -> None:
    publisher = publisher_module()
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(ProjectedArtifact(path="generated.md", ownership=OwnershipMode.FORGE_OWNED, content="new"),),
        repository_state=(),
    )

    with pytest.raises(publisher.AdapterPublicationError):
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(("generated.md", digest_content("different"))),
        )

    assert not (tmp_path / "generated.md").exists()
    assert not (tmp_path / ".forge/adapters/example/installation.yml").exists()


def test_publication_failure_rolls_back_files_and_never_publishes_installation_record(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    publisher = publisher_module()
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(path="a.md", ownership=OwnershipMode.FORGE_OWNED, content="a"),
            ProjectedArtifact(path="b.md", ownership=OwnershipMode.FORGE_OWNED, content="b"),
        ),
        repository_state=(),
    )
    original_replace = publisher._replace_file
    calls = 0

    def fail_second(path: Path, content: str) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated publication failure")
        original_replace(path, content)

    monkeypatch.setattr(publisher, "_replace_file", fail_second)

    with pytest.raises(publisher.AdapterPublicationError):
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(("a.md", digest_content("a")), ("b.md", digest_content("b"))),
        )

    assert not (tmp_path / "a.md").exists()
    assert not (tmp_path / "b.md").exists()
    assert not (tmp_path / ".forge/adapters/example/installation.yml").exists()


def test_unchanged_forge_owned_content_is_skipped_and_remains_in_the_record(
    tmp_path: Path,
) -> None:
    publisher = publisher_module()
    target = tmp_path / "generated.md"
    target.write_text("same", encoding="utf-8")
    _write_prior_record(tmp_path, ("generated.md", digest_content("same")))
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(
                path="generated.md",
                ownership=OwnershipMode.FORGE_OWNED,
                content="same",
            ),
        ),
        repository_state=(
            RepositoryArtifactState(
                path="generated.md",
                exists=True,
                current_digest=digest_content("same"),
                expected_digest=digest_content("same"),
            ),
        ),
    )

    assert plan.operations[0].intent is OperationIntent.UNCHANGED

    publisher.publish_adapter_plan(
        tmp_path,
        plan,
        _record(("generated.md", digest_content("same"))),
    )

    assert target.read_text(encoding="utf-8") == "same"
    assert (tmp_path / ".forge/adapters/example/installation.yml").exists()


def test_all_unchanged_operations_preserve_the_existing_installation_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher = publisher_module()
    target = tmp_path / "generated.md"
    target.write_text("same", encoding="utf-8")
    record = _record(("generated.md", digest_content("same")))
    installation_path = tmp_path / ".forge/adapters/example/installation.yml"
    write_installation_record(installation_path, record)
    previous_record_bytes = installation_path.read_bytes()
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(
                path="generated.md",
                ownership=OwnershipMode.FORGE_OWNED,
                content="same",
            ),
        ),
        repository_state=(
            RepositoryArtifactState(
                path="generated.md",
                exists=True,
                current_digest=digest_content("same"),
                expected_digest=digest_content("same"),
            ),
        ),
    )

    def fail_if_record_is_rewritten(path: Path, record: AdapterInstallationRecord) -> None:
        raise OSError("unchanged publication rewrote installation state")

    monkeypatch.setattr(
        publisher,
        "_write_installation_record_atomically",
        fail_if_record_is_rewritten,
    )

    publisher.publish_adapter_plan(tmp_path, plan, record)

    assert target.read_text(encoding="utf-8") == "same"
    assert installation_path.read_bytes() == previous_record_bytes


def test_failure_after_create_update_and_delete_restores_every_file_and_installation_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher = publisher_module()
    update_target = tmp_path / "update.md"
    delete_target = tmp_path / "delete.md"
    update_target.write_text("old update", encoding="utf-8")
    delete_target.write_text("old delete", encoding="utf-8")
    installation_path = tmp_path / ".forge/adapters/example/installation.yml"
    write_installation_record(
        installation_path,
        _record(
            ("delete.md", digest_content("old delete")),
            ("update.md", digest_content("old update")),
        ),
    )
    before = {
        path: path.read_bytes()
        for path in (update_target, delete_target, installation_path)
    }
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(
                path="create.md",
                ownership=OwnershipMode.FORGE_OWNED,
                content="new create",
            ),
            ProjectedArtifact(
                path="update.md",
                ownership=OwnershipMode.FORGE_OWNED,
                content="new update",
            ),
        ),
        repository_state=(
            RepositoryArtifactState(
                path="delete.md",
                exists=True,
                current_digest=digest_content("old delete"),
                expected_digest=digest_content("old delete"),
            ),
            RepositoryArtifactState(
                path="update.md",
                exists=True,
                current_digest=digest_content("old update"),
                expected_digest=digest_content("old update"),
            ),
        ),
        previous_generated=(
            GeneratedArtifact("delete.md", digest_content("old delete")),
            GeneratedArtifact("update.md", digest_content("old update")),
        ),
    )
    record_write_attempted = False

    def fail_after_operations(path: Path, record: AdapterInstallationRecord) -> None:
        nonlocal record_write_attempted
        record_write_attempted = True
        raise OSError("simulated failure after create/update/delete")

    monkeypatch.setattr(
        publisher,
        "_write_installation_record_atomically",
        fail_after_operations,
    )

    with pytest.raises(publisher.AdapterPublicationError):
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(
                ("create.md", digest_content("new create")),
                ("update.md", digest_content("new update")),
            ),
        )

    assert not (tmp_path / "create.md").exists()
    assert {path: path.read_bytes() for path in before} == before
    assert record_write_attempted is True


def test_deleting_generated_tree_leaves_separate_canonical_forge_tree_byte_identical(
    tmp_path: Path,
) -> None:
    publisher = publisher_module()
    canonical_root = tmp_path / "canonical-forge"
    canonical_files = {
        canonical_root / ".forge/project.yml": b"protocol: 1\n",
        canonical_root / ".forge/flows/default.yml": b"id: default\n",
        canonical_root / ".forge/contracts/project.yml": b"name: project\n",
        canonical_root / ".forge/changes/CHG-0008/status.yml": b"status: active\n",
    }
    for path, content in canonical_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    canonical_before = {path: path.read_bytes() for path in canonical_files}

    generated_root = tmp_path / "generated-tree"
    generated_path = generated_root / ".agents/skills/forge/SKILL.md"
    generated_path.parent.mkdir(parents=True)
    generated_path.write_text("generated skill", encoding="utf-8")
    _write_prior_record(
        generated_root,
        (".agents/skills/forge/SKILL.md", digest_content("generated skill")),
        publication_root=".agents/skills/forge",
    )
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(),
        repository_state=(
            RepositoryArtifactState(
                path=".agents/skills/forge/SKILL.md",
                exists=True,
                current_digest=digest_content("generated skill"),
                expected_digest=digest_content("generated skill"),
            ),
        ),
        previous_generated=(
            GeneratedArtifact(
                ".agents/skills/forge/SKILL.md",
                digest_content("generated skill"),
            ),
        ),
    )

    publisher.publish_adapter_plan(
        generated_root,
        plan,
        _record(publication_root=".agents/skills/forge"),
    )

    assert not generated_path.exists()
    assert generated_root.exists()
    assert {path: path.read_bytes() for path in canonical_files} == canonical_before


def test_publisher_rejects_recorded_canonical_path_outside_publication_root(
    tmp_path: Path,
) -> None:
    publisher = publisher_module()
    canonical = tmp_path / ".forge/forge.yml"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("canonical\n", encoding="utf-8")
    digest = digest_content("canonical\n")
    prior = _record(
        (".forge/forge.yml", digest),
        publication_root=".agents/skills/forge",
    )
    installation_path = tmp_path / ".forge/adapters/example/installation.yml"
    write_installation_record(installation_path, prior)
    before = {
        canonical: canonical.read_bytes(),
        installation_path: installation_path.read_bytes(),
    }
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(),
        repository_state=(
            RepositoryArtifactState(
                path=".forge/forge.yml",
                exists=True,
                current_digest=digest,
                expected_digest=digest,
            ),
        ),
        previous_generated=(GeneratedArtifact(".forge/forge.yml", digest),),
    )

    with pytest.raises(publisher.AdapterPublicationError):
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(publication_root=".agents/skills/forge"),
        )

    assert {path: path.read_bytes() for path in before} == before


def test_incomplete_rollback_reports_generic_publication_failure_and_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher = publisher_module()
    created = tmp_path / "created.md"
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(
                path="created.md",
                ownership=OwnershipMode.FORGE_OWNED,
                content="created",
            ),
        ),
        repository_state=(),
    )

    def fail_record_write(path: Path, record: AdapterInstallationRecord) -> None:
        raise OSError("simulated record write failure")

    def fail_restore(path: Path, content: bytes | None) -> None:
        raise OSError("simulated restore failure")

    monkeypatch.setattr(publisher, "_write_installation_record_atomically", fail_record_write)
    monkeypatch.setattr(publisher, "_restore_bytes", fail_restore)

    with pytest.raises(publisher.AdapterPublicationError) as raised:
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(("created.md", digest_content("created"))),
        )

    error = raised.value
    assert type(error).__name__ == "AdapterPublicationRollbackError"
    assert str(error.__cause__) == "simulated record write failure"
    assert [failure.target for failure in getattr(error, "rollback_failures", ())] == [
        "created.md",
    ]
    assert "created.md" in str(error)
    assert created.exists()


def test_incomplete_rollback_preserves_late_conflict_as_the_public_cause(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher = publisher_module()
    created = tmp_path / "a-created.md"
    updated = tmp_path / "b-updated.md"
    updated.write_text("old", encoding="utf-8")
    _write_prior_record(tmp_path, ("b-updated.md", digest_content("old")))
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(
                path="a-created.md",
                ownership=OwnershipMode.FORGE_OWNED,
                content="created",
            ),
            ProjectedArtifact(
                path="b-updated.md",
                ownership=OwnershipMode.FORGE_OWNED,
                content="new",
            ),
        ),
        repository_state=(
            RepositoryArtifactState(
                path="b-updated.md",
                exists=True,
                current_digest=digest_content("old"),
                expected_digest=digest_content("old"),
            ),
        ),
    )
    original_replace = publisher._replace_file
    original_restore = publisher._restore_bytes

    def create_then_drift(path: Path, content: str) -> None:
        original_replace(path, content)
        if path == created:
            updated.write_text("changed after planning", encoding="utf-8")

    def fail_restore(path: Path, content: bytes | None) -> None:
        if path == created:
            raise OSError("simulated restore failure")
        original_restore(path, content)

    monkeypatch.setattr(publisher, "_replace_file", create_then_drift)
    monkeypatch.setattr(publisher, "_restore_bytes", fail_restore)

    with pytest.raises(publisher.AdapterPublicationError) as raised:
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(
                ("a-created.md", digest_content("created")),
                ("b-updated.md", digest_content("new")),
            ),
        )

    error = raised.value
    assert type(error).__name__ == "AdapterPublicationRollbackError"
    assert type(error.__cause__).__name__ == "AdapterPublicationConflictError"
    assert [failure.target for failure in getattr(error, "rollback_failures", ())] == [
        "a-created.md",
    ]
    assert "a-created.md" in str(error)
    assert created.exists()
