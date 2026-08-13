from __future__ import annotations

from pathlib import Path

import pytest

from forge_cli.adapters.configuration import AdapterConfiguration, write_adapter_configuration
from forge_cli.adapters.packaged import build_packaged_registry
from forge_cli.adapters.service import (
    AdapterAlreadyInstalledError,
    AdapterDriftError,
    AdapterInstallationRequiredError,
    AdapterService,
    InvalidAdapterInstallationError,
)
from forge_cli.adapters.state import (
    AdapterInstallationRecord,
    GeneratedArtifact,
    load_installation_record,
    write_installation_record,
)
from forge_cli.adapters.manifest import IncompatibleAdapterProtocolError
from forge_cli.adapters.manifest import AdapterManifest
from forge_cli.adapters.registry import AdapterRegistry
from forge_cli.adapters.codex.driver import CodexDriver
from forge_cli.adapters.plan import digest_content


def _tree_bytes_and_mtimes(root: Path) -> dict[str, tuple[bytes, int]]:
    return {
        path.relative_to(root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@pytest.fixture
def initialized_project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    forge = root / ".forge"
    (forge / "flows").mkdir(parents=True)
    (forge / "forge.yml").write_text(
        """schema: forge/project@1
project:
  name: project
forge:
  protocol: 1
flows:
  default: standard
  allow_fast: true
  auto_escalation: true
testing:
  approach: tdd_first
review:
  strict: true
documentation:
  impact_evaluation: required
""",
        encoding="utf-8",
    )
    for flow in ("fast", "standard", "full"):
        (forge / "flows" / f"{flow}.yml").write_text(
            f"schema: forge/project-flow@1\nflow:\n  canonical: {flow}\n  enabled: true\n",
            encoding="utf-8",
        )
    return root


def _service() -> AdapterService:
    return AdapterService(build_packaged_registry())


def _installed_service(initialized_project: Path) -> AdapterService:
    service = _service()
    assert service.install(initialized_project, "codex").mutated
    return service


def _record_path(project_root: Path) -> Path:
    return project_root / ".forge" / "adapters" / "codex" / "installation.yml"


def test_plan_is_read_only_and_uses_evidence_target(initialized_project: Path) -> None:
    before = _tree_bytes_and_mtimes(initialized_project)

    result = _service().plan(initialized_project, "codex")

    assert result.target == ".agents/skills/forge"
    assert result.target_source == "evidence"
    assert result.installed_version is None
    assert result.current_version == "0.1.0"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_target_precedence_reports_explicit_configuration_then_evidence(
    initialized_project: Path,
) -> None:
    service = _service()
    write_adapter_configuration(
        initialized_project,
        AdapterConfiguration(adapter_id="codex", target="configured/codex"),
    )

    configured = service.plan(initialized_project, "codex")
    explicit = service.plan(initialized_project, "codex", explicit_target="explicit/codex")

    assert (configured.target, configured.target_source) == ("configured/codex", "configuration")
    assert (explicit.target, explicit.target_source) == ("explicit/codex", "explicit")


def test_install_then_reinstall_is_true_noop(initialized_project: Path) -> None:
    service = _service()

    first = service.install(initialized_project, "codex")
    before = _tree_bytes_and_mtimes(initialized_project)
    second = service.install(initialized_project, "codex")

    assert first.mutated is True
    assert second.mutated is False
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_install_rejects_an_existing_different_adapter_version_without_mutation(
    initialized_project: Path,
) -> None:
    service = _installed_service(initialized_project)
    record_path = _record_path(initialized_project)
    record = load_installation_record(record_path)
    write_installation_record(
        record_path,
        AdapterInstallationRecord(
            adapter_id=record.adapter_id,
            adapter_version="0.0.9",
            harness=record.harness,
            protocol_min=record.protocol_min,
            protocol_max_exclusive=record.protocol_max_exclusive,
            generated_artifacts=record.generated_artifacts,
            limitations=record.limitations,
        ),
    )
    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(AdapterAlreadyInstalledError) as error:
        service.install(initialized_project, "codex")

    assert error.value.code == "E_FORGE_ADAPTER_ALREADY_INSTALLED"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_update_refreshes_an_older_record_even_when_all_artifacts_are_unchanged(
    initialized_project: Path,
) -> None:
    service = _installed_service(initialized_project)
    path = _record_path(initialized_project)
    record = load_installation_record(path)
    write_installation_record(
        path,
        AdapterInstallationRecord(
            adapter_id=record.adapter_id,
            adapter_version="0.0.9",
            harness=record.harness,
            protocol_min=record.protocol_min,
            protocol_max_exclusive=record.protocol_max_exclusive,
            generated_artifacts=record.generated_artifacts,
            limitations=record.limitations,
        ),
    )

    result = service.update(initialized_project, "codex")

    assert result.mutated is True
    assert load_installation_record(path).adapter_version == "0.1.0"


def test_update_deletes_an_intact_obsolete_recorded_artifact(
    initialized_project: Path,
) -> None:
    service = _installed_service(initialized_project)
    path = _record_path(initialized_project)
    record = load_installation_record(path)
    obsolete = initialized_project / ".agents/skills/forge/obsolete.md"
    obsolete.write_text("obsolete\n", encoding="utf-8")
    write_installation_record(
        path,
        AdapterInstallationRecord(
            adapter_id=record.adapter_id,
            adapter_version="0.0.9",
            harness=record.harness,
            protocol_min=record.protocol_min,
            protocol_max_exclusive=record.protocol_max_exclusive,
            generated_artifacts=(
                *record.generated_artifacts,
                GeneratedArtifact(
                    path=".agents/skills/forge/obsolete.md",
                    digest=digest_content("obsolete\n"),
                ),
            ),
            limitations=record.limitations,
        ),
    )

    result = service.update(initialized_project, "codex")
    updated = load_installation_record(path)

    assert result.mutated is True
    assert not obsolete.exists()
    assert ".agents/skills/forge/obsolete.md" not in {
        artifact.path for artifact in updated.generated_artifacts
    }


def test_update_refuses_drift_without_partial_mutation(initialized_project: Path) -> None:
    service = _installed_service(initialized_project)
    skill = initialized_project / ".agents/skills/forge/SKILL.md"
    skill.write_text("user edit\n", encoding="utf-8")
    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(AdapterDriftError) as error:
        service.update(initialized_project, "codex")

    assert error.value.code == "E_FORGE_ADAPTER_DRIFT"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_update_requires_an_existing_record_without_mutation(initialized_project: Path) -> None:
    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(AdapterInstallationRequiredError) as error:
        _service().update(initialized_project, "codex")

    assert error.value.code == "E_FORGE_ADAPTER_NOT_INSTALLED"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_update_rejects_wrong_record_identity_without_mutation(initialized_project: Path) -> None:
    service = _installed_service(initialized_project)
    path = _record_path(initialized_project)
    record = load_installation_record(path)
    write_installation_record(
        path,
        AdapterInstallationRecord(
            adapter_id="other",
            adapter_version=record.adapter_version,
            harness=record.harness,
            protocol_min=record.protocol_min,
            protocol_max_exclusive=record.protocol_max_exclusive,
            generated_artifacts=record.generated_artifacts,
            limitations=record.limitations,
        ),
    )
    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(InvalidAdapterInstallationError) as error:
        service.update(initialized_project, "codex")

    assert error.value.code == "E_FORGE_ADAPTER_INSTALLATION_INVALID"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_update_rejects_an_unsafe_recorded_path_as_invalid_state_without_mutation(
    initialized_project: Path,
) -> None:
    path = _record_path(initialized_project)
    path.parent.mkdir(parents=True)
    write_installation_record(
        path,
        AdapterInstallationRecord(
            adapter_id="codex",
            adapter_version="0.0.9",
            harness="codex",
            protocol_min=1,
            protocol_max_exclusive=2,
            generated_artifacts=(GeneratedArtifact(path="../outside.md", digest="a" * 64),),
            limitations=(),
        ),
    )
    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(InvalidAdapterInstallationError) as error:
        _service().update(initialized_project, "codex")

    assert error.value.code == "E_FORGE_ADAPTER_INSTALLATION_INVALID"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_update_rejects_duplicate_recorded_paths_without_mutation(
    initialized_project: Path,
) -> None:
    path = _record_path(initialized_project)
    path.parent.mkdir(parents=True)
    write_installation_record(
        path,
        AdapterInstallationRecord(
            adapter_id="codex",
            adapter_version="0.0.9",
            harness="codex",
            protocol_min=1,
            protocol_max_exclusive=2,
            generated_artifacts=(
                GeneratedArtifact(path=".agents/skills/forge/SKILL.md", digest="a" * 64),
                GeneratedArtifact(path=".agents/skills/forge/SKILL.md", digest="b" * 64),
            ),
            limitations=(),
        ),
    )
    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(InvalidAdapterInstallationError) as error:
        _service().update(initialized_project, "codex")

    assert error.value.code == "E_FORGE_ADAPTER_INSTALLATION_INVALID"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_incompatible_protocol_fails_before_install_mutation(initialized_project: Path) -> None:
    class IncompatibleDriver:
        manifest = AdapterManifest(
            adapter_id="codex",
            version="0.1.0",
            harness="codex",
            protocol_min=2,
            protocol_max_exclusive=3,
            capabilities={},
        )
        default_target = ".agents/skills/forge"

        def project(self, context: object) -> object:
            return CodexDriver().project(context)  # type: ignore[arg-type]

    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(IncompatibleAdapterProtocolError):
        AdapterService(AdapterRegistry((IncompatibleDriver(),))).install(initialized_project, "codex")

    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_install_dry_run_is_read_only_and_returns_the_install_plan(initialized_project: Path) -> None:
    before = _tree_bytes_and_mtimes(initialized_project)

    result = _service().install(initialized_project, "codex", dry_run=True)

    assert result.mutated is False
    assert result.plan.operations
    assert _tree_bytes_and_mtimes(initialized_project) == before
