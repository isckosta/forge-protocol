from __future__ import annotations

from pathlib import Path

import pytest

from forge_cli.adapters.configuration import AdapterConfiguration, write_adapter_configuration
from forge_cli.adapters.packaged import build_packaged_registry
from forge_cli.adapters.service import (
    AdapterAlreadyInstalledError,
    AdapterDriftError,
    AdapterFlowConfigurationError,
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
from forge_cli.adapters.driver import AdapterProjection
from forge_cli.adapters.plan import digest_content
from forge_cli.adapters.validation import AdapterRepresentation


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


@pytest.fixture
def protocol2_project(initialized_project: Path) -> Path:
    configuration_path = initialized_project / ".forge" / "forge.yml"
    configuration_path.write_text(
        configuration_path.read_text(encoding="utf-8").replace("protocol: 1", "protocol: 2"),
        encoding="utf-8",
    )
    return initialized_project


def _service() -> AdapterService:
    return AdapterService(build_packaged_registry())


def _installed_service(initialized_project: Path) -> AdapterService:
    service = _service()
    assert service.install(initialized_project, "codex").mutated
    return service


def _record_path(project_root: Path) -> Path:
    return project_root / ".forge" / "adapters" / "codex" / "installation.yml"


class _EmptyDriver:
    manifest = AdapterManifest(
        adapter_id="empty",
        version="1.0.0",
        harness="empty",
        protocol_min=1,
        protocol_max_exclusive=2,
        capabilities={},
    )
    default_target = "empty"

    def validate_publication_root(self, publication_root: str) -> None:
        if publication_root != self.default_target:
            raise ValueError(publication_root)

    def project(self, context: object) -> AdapterProjection:
        return AdapterProjection(
            artifacts=(),
            limitations=(),
            representation=AdapterRepresentation(
                stages=(),
                gates=(),
                represented_invariants=(),
                enforced_invariants=(),
                limitations=(),
                repository_authority_preserved=True,
            ),
        )


def _empty_service() -> AdapterService:
    return AdapterService(AdapterRegistry((_EmptyDriver(),)))


def _empty_record_path(project_root: Path) -> Path:
    return project_root / ".forge" / "adapters" / "empty" / "installation.yml"


def test_plan_rejects_duplicate_enabled_canonical_flow_with_stable_code(
    initialized_project: Path,
) -> None:
    duplicate = initialized_project / ".forge" / "flows" / "full-duplicate.yml"
    duplicate.write_text(
        "schema: forge/project-flow@1\nflow:\n  canonical: full\n  enabled: true\n",
        encoding="utf-8",
    )

    with pytest.raises(AdapterFlowConfigurationError):
        _service().plan(initialized_project, "codex")


def test_plan_is_read_only_and_uses_evidence_target(initialized_project: Path) -> None:
    before = _tree_bytes_and_mtimes(initialized_project)

    result = _service().plan(initialized_project, "codex")

    assert result.target == ".agents/skills/forge"
    assert result.target_source == "evidence"
    assert result.installed_version is None
    assert result.current_version == "0.1.0"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_install_projects_protocol1_skill_without_reviewer_resolver_independence(
    initialized_project: Path,
) -> None:
    _service().install(initialized_project, "codex")

    skill = (initialized_project / ".agents/skills/forge/SKILL.md").read_text(encoding="utf-8")

    assert "Reviewer/Resolver independence" not in skill
    assert "subject_provenance" not in skill


def test_install_projects_protocol2_skill_with_reviewer_resolver_independence(
    protocol2_project: Path,
) -> None:
    _service().install(protocol2_project, "codex")

    skill = (protocol2_project / ".agents/skills/forge/SKILL.md").read_text(encoding="utf-8")

    assert "Reviewer/Resolver independence" in skill
    assert "Execution and Execution Context independent" in skill
    assert "subject_provenance" in skill


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


def test_empty_projection_first_install_publishes_an_empty_record(
    initialized_project: Path,
) -> None:
    result = _empty_service().install(initialized_project, "empty")

    record = load_installation_record(_empty_record_path(initialized_project))
    assert result.mutated is True
    assert record.adapter_id == "empty"
    assert record.generated_artifacts == ()


def test_empty_projection_reinstall_is_a_true_noop(initialized_project: Path) -> None:
    service = _empty_service()
    assert service.install(initialized_project, "empty").mutated is True
    before = _tree_bytes_and_mtimes(initialized_project)

    result = service.install(initialized_project, "empty")

    assert result.mutated is False
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_empty_projection_current_version_update_is_a_true_noop(
    initialized_project: Path,
) -> None:
    service = _empty_service()
    assert service.install(initialized_project, "empty").mutated is True
    before = _tree_bytes_and_mtimes(initialized_project)

    result = service.update(initialized_project, "empty")

    assert result.mutated is False
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
            publication_root=record.publication_root,
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
            publication_root=record.publication_root,
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
            publication_root=record.publication_root,
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


def test_update_rejects_explicitly_rooted_record_claiming_canonical_forge_state(
    initialized_project: Path,
) -> None:
    service = _installed_service(initialized_project)
    record_path = _record_path(initialized_project)
    record = load_installation_record(record_path)
    canonical = initialized_project / ".forge/forge.yml"
    write_installation_record(
        record_path,
        AdapterInstallationRecord(
            adapter_id=record.adapter_id,
            adapter_version="0.0.9",
            harness=record.harness,
            protocol_min=record.protocol_min,
            protocol_max_exclusive=record.protocol_max_exclusive,
            publication_root=record.publication_root,
            generated_artifacts=(
                *record.generated_artifacts,
                GeneratedArtifact(
                    path=".forge/forge.yml",
                    digest=digest_content(canonical.read_text(encoding="utf-8")),
                ),
            ),
            limitations=record.limitations,
        ),
    )
    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(InvalidAdapterInstallationError):
        service.update(initialized_project, "codex")

    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_plan_rejects_installed_publication_root_mismatch_without_cleanup(
    initialized_project: Path,
) -> None:
    service = _installed_service(initialized_project)
    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(InvalidAdapterInstallationError):
        service.plan(
            initialized_project,
            "codex",
            explicit_target="another/codex-root",
        )

    assert _tree_bytes_and_mtimes(initialized_project) == before


def _write_hostile_canonical_paths_to_older_record(project_root: Path) -> None:
    canonical_files = {
        ".forge/contract.yml": "schema: forge/contract@1\nreview:\n  strict: true\n",
        ".forge/changes/CHG-HOSTILE/specification.md": "# Canonical change\n",
    }
    for relative_path, content in canonical_files.items():
        path = project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    record_path = _record_path(project_root)
    record = load_installation_record(record_path)
    protected_paths = (
        ".forge/forge.yml",
        ".forge/flows/standard.yml",
        *canonical_files,
    )
    hostile_artifacts = tuple(
        GeneratedArtifact(
            path=relative_path,
            digest=digest_content((project_root / relative_path).read_text(encoding="utf-8")),
        )
        for relative_path in protected_paths
    )
    write_installation_record(
        record_path,
        AdapterInstallationRecord(
            adapter_id=record.adapter_id,
            adapter_version="0.0.9",
            harness=record.harness,
            protocol_min=record.protocol_min,
            protocol_max_exclusive=record.protocol_max_exclusive,
            generated_artifacts=(*record.generated_artifacts, *hostile_artifacts),
            limitations=record.limitations,
        ),
    )


def test_plan_rejects_recorded_canonical_forge_paths_without_planning_deletion(
    initialized_project: Path,
) -> None:
    """Catch record trust that can classify canonical Forge state as generated cleanup."""
    service = _installed_service(initialized_project)
    _write_hostile_canonical_paths_to_older_record(initialized_project)
    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(InvalidAdapterInstallationError) as error:
        service.plan(initialized_project, "codex")

    assert error.value.code == "E_FORGE_ADAPTER_INSTALLATION_INVALID"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_update_rejects_recorded_canonical_forge_paths_without_mutation(
    initialized_project: Path,
) -> None:
    """Catch publisher authorization of canonical deletion through a hostile record."""
    service = _installed_service(initialized_project)
    _write_hostile_canonical_paths_to_older_record(initialized_project)
    before = _tree_bytes_and_mtimes(initialized_project)
    caught: InvalidAdapterInstallationError | None = None

    try:
        service.update(initialized_project, "codex")
    except InvalidAdapterInstallationError as error:
        caught = error

    assert _tree_bytes_and_mtimes(initialized_project) == before
    assert caught is not None
    assert caught.code == "E_FORGE_ADAPTER_INSTALLATION_INVALID"


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
            publication_root=record.publication_root,
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
            publication_root=".agents/skills/forge",
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
            publication_root=".agents/skills/forge",
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

        def validate_publication_root(self, publication_root: str) -> None:
            if publication_root != self.default_target:
                raise ValueError(publication_root)

        def project(self, context: object) -> object:
            return CodexDriver().project(context)  # type: ignore[arg-type]

    before = _tree_bytes_and_mtimes(initialized_project)

    with pytest.raises(IncompatibleAdapterProtocolError):
        AdapterService(AdapterRegistry((IncompatibleDriver(),))).install(initialized_project, "codex")

    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_doctor_rejects_unsupported_project_protocol_even_when_driver_range_includes_it(
    initialized_project: Path,
) -> None:
    configuration_path = initialized_project / ".forge" / "forge.yml"
    configuration_path.write_text(
        configuration_path.read_text(encoding="utf-8").replace("protocol: 1", "protocol: 99"),
        encoding="utf-8",
    )

    class NumericallyCompatibleDriver:
        manifest = AdapterManifest(
            adapter_id="wide-range",
            version="1.0.0",
            harness="fixture",
            protocol_min=1,
            protocol_max_exclusive=100,
            capabilities={},
        )
        default_target = "generated/fixture"

        def validate_publication_root(self, publication_root: str) -> None:
            if publication_root != self.default_target:
                raise ValueError(publication_root)

        def project(self, context: object) -> AdapterProjection:
            raise AssertionError("Unsupported project configuration must not reach projection.")

    service = AdapterService(AdapterRegistry((NumericallyCompatibleDriver(),)))
    before = _tree_bytes_and_mtimes(initialized_project)

    doctor = service.doctor(initialized_project, "wide-range")
    validation = service.validate(initialized_project, "wide-range")

    configuration = next(item for item in doctor.checks if item.id == "configuration")
    compatibility = next(item for item in doctor.checks if item.id == "compatibility")
    assert configuration.status == "failed"
    assert configuration.code == "E_FORGE_UNSUPPORTED_PROTOCOL"
    assert "Set `.forge/forge.yml` to a supported Forge Protocol" in configuration.remediation
    assert compatibility.status == "warning"
    assert compatibility.code == "W_FORGE_ADAPTER_COMPATIBILITY_UNAVAILABLE"
    assert doctor.passed is False
    assert validation.passed is False
    assert validation.findings[0].id == "configuration"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_install_dry_run_is_read_only_and_returns_the_install_plan(initialized_project: Path) -> None:
    before = _tree_bytes_and_mtimes(initialized_project)

    result = _service().install(initialized_project, "codex", dry_run=True)

    assert result.mutated is False
    assert result.plan.operations
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_doctor_reports_drift_and_action_without_mutating(initialized_project: Path) -> None:
    service = _installed_service(initialized_project)
    skill = initialized_project / ".agents/skills/forge/SKILL.md"
    skill.write_text("user edit\n", encoding="utf-8")
    before = _tree_bytes_and_mtimes(initialized_project)

    result = service.doctor(initialized_project, "codex")

    assert result.passed is False
    drift = next(item for item in result.checks if item.id == "generated_drift")
    assert drift.status == "failed"
    assert "restore the recorded artifact" in drift.remediation
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_validate_converts_doctor_failures_to_stable_findings_without_mutating(
    initialized_project: Path,
) -> None:
    before = _tree_bytes_and_mtimes(initialized_project)

    result = _service().validate(initialized_project, "codex")

    assert result.passed is False
    assert [(item.id, item.code) for item in result.findings] == [
        ("installation", "E_FORGE_ADAPTER_NOT_INSTALLED"),
    ]
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_doctor_is_deterministic_and_limitations_do_not_fail_an_intact_installation(
    initialized_project: Path,
) -> None:
    service = _installed_service(initialized_project)
    before = _tree_bytes_and_mtimes(initialized_project)

    first = service.doctor(initialized_project, "codex")
    second = service.doctor(initialized_project, "codex")
    validation = service.validate(initialized_project, "codex")

    assert first == second
    assert [item.id for item in first.checks] == [
        "configuration",
        "compatibility",
        "target",
        "installation",
        "generated_drift",
        "executable_artifacts",
        "conformance",
        "limitations",
    ]
    assert first.passed is True
    assert any(item.status == "warning" for item in first.checks)
    assert validation.passed is True
    assert validation.findings == ()
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_doctor_distinguishes_a_missing_recorded_artifact_without_mutating(
    initialized_project: Path,
) -> None:
    service = _installed_service(initialized_project)
    (initialized_project / ".agents/skills/forge/SKILL.md").unlink()
    before = _tree_bytes_and_mtimes(initialized_project)

    result = service.doctor(initialized_project, "codex")

    drift = next(item for item in result.checks if item.id == "generated_drift")
    assert drift.status == "failed"
    assert "missing" in drift.message
    assert "restore the recorded artifact" in drift.remediation
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_validate_reports_generic_conformance_failure_without_mutating(
    initialized_project: Path,
) -> None:
    class NonconformantDriver:
        manifest = AdapterManifest(
            adapter_id="nonconformant",
            version="1.0.0",
            harness="fixture",
            protocol_min=1,
            protocol_max_exclusive=2,
            capabilities={},
        )
        default_target = "generated/fixture"

        def validate_publication_root(self, publication_root: str) -> None:
            if publication_root != self.default_target:
                raise ValueError(publication_root)

        def project(self, context: object) -> AdapterProjection:
            return AdapterProjection(
                artifacts=(),
                limitations=(),
                representation=AdapterRepresentation(
                    stages=(),
                    gates=(),
                    represented_invariants=(),
                    enforced_invariants=(),
                    limitations=(),
                    repository_authority_preserved=True,
                    red_before_behavior_preserved=False,
                    strict_review_preserved=False,
                ),
            )

    service = AdapterService(AdapterRegistry((NonconformantDriver(),)))
    before = _tree_bytes_and_mtimes(initialized_project)

    result = service.validate(initialized_project, "nonconformant")

    conformance = next(item for item in result.findings if item.id == "conformance")
    assert conformance.code == "E_FORGE_ADAPTER_CONFORMANCE"
    assert _tree_bytes_and_mtimes(initialized_project) == before


def test_doctor_reports_unsafe_recorded_generated_paths_without_mutating(
    initialized_project: Path,
) -> None:
    path = _record_path(initialized_project)
    path.parent.mkdir(parents=True)
    write_installation_record(
        path,
        AdapterInstallationRecord(
            adapter_id="codex",
            adapter_version="0.1.0",
            harness="codex",
            protocol_min=1,
            protocol_max_exclusive=2,
            publication_root=".agents/skills/forge",
            generated_artifacts=(GeneratedArtifact(path="../outside.md", digest="a" * 64),),
            limitations=(),
        ),
    )
    before = _tree_bytes_and_mtimes(initialized_project)

    result = _service().doctor(initialized_project, "codex")

    drift = next(item for item in result.checks if item.id == "generated_drift")
    assert drift.status == "failed"
    assert drift.code == "E_FORGE_ADAPTER_INSTALLATION_INVALID"
    assert "unsafe" in drift.message.lower()
    assert _tree_bytes_and_mtimes(initialized_project) == before


# --- CHG-0049: executable hook materialization / diagnostics / repair -------

import os as _os
import stat as _stat

_posix_only = pytest.mark.skipif(
    _os.name != "posix", reason="executable-bit behaviour is POSIX-only"
)

_HOOK = ".claude/skills/forge/hooks/check-manifest-edit.sh"


def _executable(path: Path) -> bool:
    return bool(_stat.S_IMODE(path.stat().st_mode) & 0o111)


@_posix_only
def test_claude_code_install_materializes_hook_executable(initialized_project: Path) -> None:
    _service().install(initialized_project, "claude-code")
    assert _executable(initialized_project / _HOOK)


@_posix_only
def test_doctor_flags_non_executable_installed_hook(initialized_project: Path) -> None:
    service = _service()
    service.install(initialized_project, "claude-code")
    (initialized_project / _HOOK).chmod(0o644)

    result = service.doctor(initialized_project, "claude-code")

    check = next(item for item in result.checks if item.id == "executable_artifacts")
    assert check.status == "failed"
    assert _HOOK in check.message
    assert "forge adapter update claude-code" in check.remediation
    assert result.passed is False


@_posix_only
def test_doctor_passes_executable_check_for_healthy_install(initialized_project: Path) -> None:
    service = _service()
    service.install(initialized_project, "claude-code")

    result = service.doctor(initialized_project, "claude-code")

    check = next(item for item in result.checks if item.id == "executable_artifacts")
    assert check.status == "passed"


@_posix_only
def test_update_repairs_non_executable_hook_idempotently(initialized_project: Path) -> None:
    service = _service()
    service.install(initialized_project, "claude-code")
    hook = initialized_project / _HOOK
    hook.chmod(0o644)

    first = service.update(initialized_project, "claude-code")
    assert first.mutated is True
    assert _executable(hook)
    # installation record still parses / validates
    load_installation_record(
        initialized_project / ".forge/adapters/claude-code/installation.yml"
    )

    second = service.update(initialized_project, "claude-code")
    assert second.mutated is False
    assert _executable(hook)


def test_doctor_executable_check_is_inert_on_non_posix(
    initialized_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = _service()
    service.install(initialized_project, "claude-code")
    monkeypatch.setattr("forge_cli.adapters.service.supports_executable_bit", lambda: False)

    result = service.doctor(initialized_project, "claude-code")

    check = next(item for item in result.checks if item.id == "executable_artifacts")
    assert check.status == "passed"
