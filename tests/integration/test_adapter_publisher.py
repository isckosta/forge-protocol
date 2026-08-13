import importlib
from pathlib import Path

import pytest

from forge_cli.adapters.manifest import AdapterManifest
from forge_cli.adapters.plan import AdapterPlan, OwnershipMode, digest_content
from forge_cli.adapters.planner import (
    EffectiveAdapterConfiguration,
    ProjectedArtifact,
    RepositoryArtifactState,
    plan_adapter,
)
from forge_cli.adapters.state import AdapterInstallationRecord, GeneratedArtifact


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


def _record(*artifacts: tuple[str, str]) -> AdapterInstallationRecord:
    return AdapterInstallationRecord(
        adapter_id="example",
        adapter_version="1.0.0",
        harness="example-harness",
        protocol_min=1,
        protocol_max_exclusive=2,
        generated_artifacts=(GeneratedArtifact(path=path, digest=digest) for path, digest in artifacts),
        limitations=(),
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
    assert not (tmp_path / ".forge/adapters/example/installation.yml").exists()


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
