import importlib
from pathlib import Path

import pytest

from forge_cli.adapters.manifest import AdapterManifest
from forge_cli.adapters.ownership import (
    InvalidAdapterPublicationOwnershipError,
    require_publication_root_ownership,
)
from forge_cli.adapters.plan import (
    AdapterOperation,
    AdapterPlan,
    OperationIntent,
    OwnershipMode,
    digest_content,
)
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


def test_directory_symlink_swap_after_preflight_prevents_escaping_publication_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publisher = publisher_module()
    outside = tmp_path.parent / "forge-outside-create-swap"
    outside.mkdir(exist_ok=True)
    tool_dir = tmp_path / "tool"
    tool_dir.mkdir()
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(ProjectedArtifact(path="tool/generated.md", ownership=OwnershipMode.FORGE_OWNED, content="escape"),),
        repository_state=(),
    )
    original_record_validation = publisher._validate_record_matches_plan

    def swap_directory_for_symlink_after_preflight(plan, record) -> None:
        original_record_validation(plan, record)
        tool_dir.rmdir()
        tool_dir.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(publisher, "_validate_record_matches_plan", swap_directory_for_symlink_after_preflight)

    with pytest.raises(publisher.AdapterPublicationError):
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(("tool/generated.md", digest_content("escape"))),
        )

    assert not (outside / "generated.md").exists()


def test_directory_symlink_swap_after_preflight_prevents_escaping_update_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publisher = publisher_module()
    outside = tmp_path.parent / "forge-outside-update-swap"
    outside.mkdir(exist_ok=True)
    canary = outside / "generated.md"
    canary.write_text("old", encoding="utf-8")

    tool_dir = tmp_path / "tool"
    tool_dir.mkdir()
    target = tool_dir / "generated.md"
    target.write_text("old", encoding="utf-8")
    _write_prior_record(tmp_path, ("tool/generated.md", digest_content("old")))

    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(ProjectedArtifact(path="tool/generated.md", ownership=OwnershipMode.FORGE_OWNED, content="new"),),
        repository_state=(RepositoryArtifactState(path="tool/generated.md", exists=True, current_digest=digest_content("old"), expected_digest=digest_content("old")),),
    )
    original_record_validation = publisher._validate_record_matches_plan

    def swap_directory_for_symlink_after_preflight(plan, record) -> None:
        original_record_validation(plan, record)
        target.unlink()
        tool_dir.rmdir()
        tool_dir.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(publisher, "_validate_record_matches_plan", swap_directory_for_symlink_after_preflight)

    with pytest.raises(publisher.AdapterPublicationError):
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(("tool/generated.md", digest_content("new"))),
        )

    assert canary.read_text(encoding="utf-8") == "old"


def test_directory_symlink_swap_after_preflight_prevents_escaping_installation_record_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publisher = publisher_module()
    outside = tmp_path.parent / "forge-outside-install-record-swap"
    outside.mkdir(exist_ok=True)
    adapter_state_dir = tmp_path / ".forge" / "adapters" / "example"
    adapter_state_dir.mkdir(parents=True)
    plan = AdapterPlan(adapter_id="example", operations=(), conflicts=())
    original_record_validation = publisher._validate_record_matches_plan

    def swap_directory_for_symlink_after_preflight(plan, record) -> None:
        original_record_validation(plan, record)
        adapter_state_dir.rmdir()
        adapter_state_dir.symlink_to(outside, target_is_directory=True)

    monkeypatch.setattr(publisher, "_validate_record_matches_plan", swap_directory_for_symlink_after_preflight)

    with pytest.raises(publisher.AdapterPublicationError):
        publisher.publish_adapter_plan(tmp_path, plan, _record())

    assert not (outside / "installation.yml").exists()


def test_stale_prior_record_authorization_mismatch_uses_stable_stale_record_code(
    tmp_path: Path,
) -> None:
    publisher = publisher_module()
    target = tmp_path / "generated.md"
    target.write_text("current", encoding="utf-8")
    _write_prior_record(tmp_path, ("generated.md", digest_content("stale-recorded-value")))
    operation = AdapterOperation(
        path="generated.md",
        ownership=OwnershipMode.FORGE_OWNED,
        intent=OperationIntent.UPDATE,
        content_digest=digest_content("new"),
        content="new",
        expected_current_digest=digest_content("current"),
    )
    plan = AdapterPlan(adapter_id="example", operations=(operation,))

    with pytest.raises(publisher.AdapterPublicationStaleRecordError):
        publisher.publish_adapter_plan(
            tmp_path, plan, _record(("generated.md", digest_content("new")))
        )

    assert target.read_text(encoding="utf-8") == "current"


def test_installation_state_directory_symlink_swap_before_first_read_cannot_forge_authorization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publisher = publisher_module()
    target = tmp_path / "generated.md"
    target.write_text("old-user-content", encoding="utf-8")

    outside = tmp_path.parent / "forge-outside-install-read-swap"
    outside.mkdir(exist_ok=True)
    forged_record = _record(("generated.md", digest_content("old-user-content")))
    write_installation_record(outside / "installation.yml", forged_record)

    adapter_state_dir = tmp_path / ".forge" / "adapters" / "example"
    adapter_state_dir.mkdir(parents=True)

    operation = AdapterOperation(
        path="generated.md",
        ownership=OwnershipMode.FORGE_OWNED,
        intent=OperationIntent.UPDATE,
        content_digest=digest_content("attacker-new-content"),
        content="attacker-new-content",
        expected_current_digest=digest_content("old-user-content"),
    )
    plan = AdapterPlan(adapter_id="example", operations=(operation,))

    original_record_validation = publisher._validate_record_matches_plan
    original_authorization_check = publisher._validate_prior_record_authorizes_plan

    def swap_directory_for_symlink_before_first_read(plan, record) -> None:
        original_record_validation(plan, record)
        adapter_state_dir.rmdir()
        adapter_state_dir.symlink_to(outside, target_is_directory=True)

    def restore_real_directory_after_the_poisoned_read(plan, next_record, prior_record) -> None:
        original_authorization_check(plan, next_record, prior_record)
        adapter_state_dir.unlink()
        adapter_state_dir.mkdir(parents=True)

    monkeypatch.setattr(
        publisher, "_validate_record_matches_plan", swap_directory_for_symlink_before_first_read
    )
    monkeypatch.setattr(
        publisher,
        "_validate_prior_record_authorizes_plan",
        restore_real_directory_after_the_poisoned_read,
    )

    with pytest.raises(publisher.AdapterPublicationError):
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(("generated.md", digest_content("attacker-new-content"))),
        )

    assert target.read_text(encoding="utf-8") == "old-user-content"


def test_rollback_backup_capture_cannot_be_poisoned_by_a_directory_swap_after_authorization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publisher = publisher_module()
    outside = tmp_path.parent / "forge-outside-backup-capture-swap"
    outside.mkdir(exist_ok=True)
    forged_record = _record(("forged.md", digest_content("forged")))
    write_installation_record(outside / "installation.yml", forged_record)

    adapter_state_dir = tmp_path / ".forge" / "adapters" / "example"
    adapter_state_dir.mkdir(parents=True)

    operation = AdapterOperation(
        path="create.md",
        ownership=OwnershipMode.FORGE_OWNED,
        intent=OperationIntent.CREATE,
        content_digest=digest_content("new"),
        content="new",
    )
    plan = AdapterPlan(adapter_id="example", operations=(operation,))

    original_authorization_check = publisher._validate_prior_record_authorizes_plan

    def swap_directory_for_symlink_after_authorization(plan, next_record, prior_record) -> None:
        original_authorization_check(plan, next_record, prior_record)
        adapter_state_dir.rmdir()
        adapter_state_dir.symlink_to(outside, target_is_directory=True)

    def restore_real_directory_and_fail_the_mutation(path) -> None:
        adapter_state_dir.unlink()
        adapter_state_dir.mkdir(parents=True)
        raise publisher.AdapterPublicationConflictError(
            "Adapter create target appeared after planning: simulated."
        )

    monkeypatch.setattr(
        publisher,
        "_validate_prior_record_authorizes_plan",
        swap_directory_for_symlink_after_authorization,
    )
    monkeypatch.setattr(
        publisher, "_reserve_create_target", restore_real_directory_and_fail_the_mutation
    )

    with pytest.raises(publisher.AdapterPublicationError):
        publisher.publish_adapter_plan(
            tmp_path, plan, _record(("create.md", digest_content("new")))
        )

    real_installation_path = tmp_path / ".forge/adapters/example/installation.yml"
    assert not real_installation_path.exists()


def test_rollback_of_an_already_applied_operation_reuses_a_stale_target_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publisher = publisher_module()
    sub = tmp_path / "sub"
    sub.mkdir()
    a_target = sub / "a.md"
    a_target.write_text("SECRET-old-a-content", encoding="utf-8")
    b_target = tmp_path / "zzz-b.md"
    b_target.write_text("old-b-content", encoding="utf-8")

    outside = tmp_path.parent / "forge-outside-rollback-applied-swap"
    outside.mkdir(exist_ok=True)
    real_sub_backup = tmp_path.parent / "sub-real-backup"

    operation_a = AdapterOperation(
        path="sub/a.md",
        ownership=OwnershipMode.FORGE_OWNED,
        intent=OperationIntent.UPDATE,
        content_digest=digest_content("new-a-content"),
        content="new-a-content",
        expected_current_digest=digest_content("SECRET-old-a-content"),
    )
    operation_b = AdapterOperation(
        path="zzz-b.md",
        ownership=OwnershipMode.FORGE_OWNED,
        intent=OperationIntent.UPDATE,
        content_digest=digest_content("new-b-content"),
        content="new-b-content",
        expected_current_digest=digest_content("old-b-content"),
    )
    plan = AdapterPlan(adapter_id="example", operations=(operation_a, operation_b))
    _write_prior_record(
        tmp_path,
        ("sub/a.md", digest_content("SECRET-old-a-content")),
        ("zzz-b.md", digest_content("old-b-content")),
    )

    original_digest_and_bytes = publisher._current_digest_and_bytes

    def swap_a_directory_aside_then_report_b_as_concurrently_changed(
        path: Path,
    ) -> tuple[str, bytes]:
        # Only the mutation loop's precondition recheck calls
        # _current_digest_and_bytes (preflight uses the digest-only
        # _current_digest), so operation_a is already applied by the time
        # this fires for operation_b.
        if path.name == "zzz-b.md":
            sub.rename(real_sub_backup)
            sub.symlink_to(outside, target_is_directory=True)
            return digest_content("concurrently-changed-by-someone-else"), b"irrelevant"
        return original_digest_and_bytes(path)

    monkeypatch.setattr(
        publisher,
        "_current_digest_and_bytes",
        swap_a_directory_aside_then_report_b_as_concurrently_changed,
    )

    with pytest.raises(publisher.AdapterPublicationError) as raised:
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(
                ("sub/a.md", digest_content("new-a-content")),
                ("zzz-b.md", digest_content("new-b-content")),
            ),
        )

    # The swapped directory makes a safe restore impossible; this must fail
    # loudly as an incomplete rollback rather than silently leaking the
    # original content to the attacker-controlled directory.
    error = raised.value
    assert type(error).__name__ == "AdapterPublicationRollbackError"
    assert [failure.target for failure in getattr(error, "rollback_failures", ())] == [
        "sub/a.md",
    ]
    assert not (outside / "a.md").exists()


def test_prior_record_read_is_not_desynchronized_by_a_concurrent_content_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publisher = publisher_module()
    installation_path = tmp_path / ".forge/adapters/example/installation.yml"
    _write_prior_record(tmp_path, ("legit.md", digest_content("legit")))
    legit_bytes = installation_path.read_bytes()

    forged_record = _record(("forged.md", digest_content("forged")))
    original_parse = publisher.parse_installation_record

    def rewrite_the_file_then_parse(text: str):
        # Simulate a racing writer that changes the on-disk content the
        # instant it is parsed, to prove parsing derives from the bytes
        # already captured rather than performing its own separate read of
        # the path -- two separate physical reads of the same file could
        # otherwise desynchronize what gets authorized from what gets
        # captured as the rollback backup, without any symlink involved.
        write_installation_record(installation_path, forged_record)
        return original_parse(text)

    monkeypatch.setattr(publisher, "parse_installation_record", rewrite_the_file_then_parse)

    record, raw = publisher._load_prior_installation_record(installation_path)

    assert raw == legit_bytes
    assert {artifact.path for artifact in record.generated_artifacts} == {"legit.md"}


def test_update_precondition_digest_and_rollback_backup_come_from_the_same_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publisher = publisher_module()
    target = tmp_path / "generated.md"
    target.write_text("SECRET-legit-content", encoding="utf-8")
    _write_prior_record(tmp_path, ("generated.md", digest_content("SECRET-legit-content")))
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(path="generated.md", ownership=OwnershipMode.FORGE_OWNED, content="new"),
        ),
        repository_state=(
            RepositoryArtifactState(
                path="generated.md",
                exists=True,
                current_digest=digest_content("SECRET-legit-content"),
                expected_digest=digest_content("SECRET-legit-content"),
            ),
        ),
    )
    original_digest_and_bytes = publisher._current_digest_and_bytes

    def rewrite_the_file_then_read(path):
        # Simulate a racing writer that changes the file the instant it is
        # inspected, to prove the digest check and the rollback-backup
        # capture derive from the same physical read.
        target.write_text("ATTACKER-RACE-INJECTED-CONTENT", encoding="utf-8")
        return original_digest_and_bytes(path)

    monkeypatch.setattr(publisher, "_current_digest_and_bytes", rewrite_the_file_then_read)

    with pytest.raises(publisher.AdapterPublicationConflictError):
        publisher.publish_adapter_plan(
            tmp_path, plan, _record(("generated.md", digest_content("new")))
        )

    assert target.read_text(encoding="utf-8") == "ATTACKER-RACE-INJECTED-CONTENT"


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

    def fail_second(path: Path, content: str, *, executable: bool = False) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated publication failure")
        original_replace(path, content, executable=executable)

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


def test_no_op_short_circuit_reuses_the_already_loaded_prior_record_instead_of_a_second_raw_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher = publisher_module()
    target = tmp_path / "generated.md"
    target.write_text("same", encoding="utf-8")
    record = _record(("generated.md", digest_content("same")))
    installation_path = tmp_path / ".forge/adapters/example/installation.yml"
    write_installation_record(installation_path, record)
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(path="generated.md", ownership=OwnershipMode.FORGE_OWNED, content="same"),
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
    original_authorization_check = publisher._validate_prior_record_authorizes_plan

    def corrupt_record_on_disk_after_the_first_safe_read(plan, next_record, prior_record) -> None:
        original_authorization_check(plan, next_record, prior_record)
        installation_path.write_text(":\n  - not [valid yaml", encoding="utf-8")

    monkeypatch.setattr(
        publisher,
        "_validate_prior_record_authorizes_plan",
        corrupt_record_on_disk_after_the_first_safe_read,
    )

    publisher.publish_adapter_plan(tmp_path, plan, record)


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


def test_publisher_rejects_shared_update_of_canonical_forge_state(
    tmp_path: Path,
) -> None:
    publisher = publisher_module()
    canonical = tmp_path / ".forge/forge.yml"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("canonical\n", encoding="utf-8")
    canonical.chmod(0o640)
    canonical_stat = canonical.stat()
    before = (
        canonical.read_bytes(),
        canonical_stat.st_mode,
        canonical_stat.st_mtime_ns,
    )
    record_path = tmp_path / ".forge/adapters/example/installation.yml"
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(
                path=".forge/forge.yml",
                ownership=OwnershipMode.SHARED,
                content="ignored projection\n",
                merge_result="shared overwrite\n",
                merge_strategy_id="test-merge-v1",
            ),
        ),
        repository_state=(
            RepositoryArtifactState(
                path=".forge/forge.yml",
                exists=True,
                current_digest=digest_content("canonical\n"),
                expected_digest=None,
            ),
        ),
    )
    assert plan.conflicts == ()
    assert plan.operations[0].intent is OperationIntent.UPDATE
    assert plan.operations[0].ownership is OwnershipMode.SHARED

    caught: Exception | None = None
    try:
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(publication_root=".agents/skills/forge"),
        )
    except publisher.AdapterPublicationError as error:
        caught = error

    observed_stat = canonical.stat()
    observed = (
        canonical.read_bytes(),
        observed_stat.st_mode,
        observed_stat.st_mtime_ns,
    )
    assert (caught is not None, observed, record_path.exists()) == (
        True,
        before,
        False,
    )


def test_publication_root_itself_is_not_an_owned_artifact_or_publishable_target(
    tmp_path: Path,
) -> None:
    publisher = publisher_module()
    ownership_error: InvalidAdapterPublicationOwnershipError | None = None
    try:
        require_publication_root_ownership("bundle", ("bundle",))
    except InvalidAdapterPublicationOwnershipError as error:
        ownership_error = error

    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(
                path="bundle",
                ownership=OwnershipMode.FORGE_OWNED,
                content="generated\n",
            ),
        ),
        repository_state=(),
    )
    publication_error: Exception | None = None
    try:
        publisher.publish_adapter_plan(
            tmp_path,
            plan,
            _record(
                ("bundle", digest_content("generated\n")),
                publication_root="bundle",
            ),
        )
    except publisher.AdapterPublicationError as error:
        publication_error = error

    assert (
        ownership_error is not None,
        publication_error is not None,
        (tmp_path / "bundle").exists(),
        (tmp_path / ".forge/adapters/example/installation.yml").exists(),
    ) == (True, True, False, False)


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

    def fail_restore(path: Path, content: bytes | None, mode: int | None = None) -> None:
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

    def create_then_drift(path: Path, content: str, *, executable: bool = False) -> None:
        original_replace(path, content, executable=executable)
        if path == created:
            updated.write_text("changed after planning", encoding="utf-8")

    def fail_restore(path: Path, content: bytes | None, mode: int | None = None) -> None:
        if path == created:
            raise OSError("simulated restore failure")
        original_restore(path, content, mode)

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


# --- CHG-0049: executable-artifact materialization -------------------------

import os as _os
import stat as _stat
import subprocess as _subprocess

posix_only = pytest.mark.skipif(
    _os.name != "posix", reason="executable-bit materialization is POSIX-only"
)


def _is_executable(path: Path) -> bool:
    return bool(_stat.S_IMODE(path.stat().st_mode) & _stat.S_IXUSR)


@posix_only
def test_executable_create_materializes_with_executable_mode(tmp_path: Path) -> None:
    publisher = publisher_module()
    script = "#!/bin/sh\necho FORGE_OK\n"
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(
                path="hooks/check.sh",
                ownership=OwnershipMode.FORGE_OWNED,
                content=script,
                executable=True,
            ),
            ProjectedArtifact(
                path="SKILL.md",
                ownership=OwnershipMode.FORGE_OWNED,
                content="# skill\n",
            ),
        ),
        repository_state=(),
    )

    publisher.publish_adapter_plan(
        tmp_path,
        plan,
        _record(
            ("SKILL.md", digest_content("# skill\n")),
            ("hooks/check.sh", digest_content(script)),
        ),
    )

    hook = tmp_path / "hooks/check.sh"
    assert hook.read_text(encoding="utf-8") == script
    assert _is_executable(hook)
    # non-executable sibling must not have been made executable
    assert not _is_executable(tmp_path / "SKILL.md")
    # the materialized script runs without Permission denied
    result = _subprocess.run([str(hook)], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.strip() == "FORGE_OK"


@posix_only
def test_executable_update_reapplies_mode_on_identical_content(tmp_path: Path) -> None:
    publisher = publisher_module()
    script = "#!/bin/sh\nexit 0\n"
    hook = tmp_path / "hooks/check.sh"
    hook.parent.mkdir(parents=True)
    hook.write_text(script, encoding="utf-8")
    hook.chmod(0o644)
    _write_prior_record(tmp_path, ("hooks/check.sh", digest_content(script)))

    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(
                path="hooks/check.sh",
                ownership=OwnershipMode.FORGE_OWNED,
                content=script,
                executable=True,
            ),
        ),
        repository_state=(
            RepositoryArtifactState(
                path="hooks/check.sh",
                exists=True,
                current_digest=digest_content(script),
                expected_digest=digest_content(script),
                executable=False,
            ),
        ),
    )
    assert plan.operations[0].intent is OperationIntent.UPDATE

    publisher.publish_adapter_plan(
        tmp_path, plan, _record(("hooks/check.sh", digest_content(script)))
    )

    assert hook.read_text(encoding="utf-8") == script
    assert _is_executable(hook)


def test_executable_publish_does_not_fail_on_non_posix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    publisher = publisher_module()
    monkeypatch.setattr("forge_cli.adapters.publisher.supports_executable_bit", lambda: False)
    script = "#!/bin/sh\nexit 0\n"
    plan = plan_adapter(
        manifest=_manifest(),
        effective_configuration=EffectiveAdapterConfiguration(1, ()),
        projections=(
            ProjectedArtifact(
                path="hooks/check.sh",
                ownership=OwnershipMode.FORGE_OWNED,
                content=script,
                executable=True,
            ),
        ),
        repository_state=(),
    )

    publisher.publish_adapter_plan(
        tmp_path, plan, _record(("hooks/check.sh", digest_content(script)))
    )

    assert (tmp_path / "hooks/check.sh").read_text(encoding="utf-8") == script
