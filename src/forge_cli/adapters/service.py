"""Generic Adapter use-case orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from forge_cli.adapters.configuration import AdapterConfiguration, load_adapter_configuration
from forge_cli.adapters.driver import AdapterProjectionContext, HarnessDriver
from forge_cli.adapters.ownership import detect_generated_drift
from forge_cli.adapters.plan import AdapterPlan, OperationIntent, OwnershipMode
from forge_cli.adapters.planner import (
    EffectiveAdapterConfiguration,
    RepositoryArtifactState,
    plan_adapter,
)
from forge_cli.adapters.publisher import publish_adapter_plan
from forge_cli.adapters.repository import (
    AdapterRepositoryError,
    InvalidAdapterRepositoryRecordError,
    load_optional_installation_record,
    snapshot_repository_artifacts,
)
from forge_cli.adapters.registry import AdapterRegistry
from forge_cli.adapters.state import AdapterInstallationRecord, GeneratedArtifact
from forge_cli.configuration import load_project_configuration
from forge_cli.protocol_resources import resolve_protocol_root
from forge_cli.protocol_resolution import resolve_effective_contract, resolve_effective_flow


class AdapterServiceError(RuntimeError):
    """Base error for Adapter service operations."""


class AdapterAlreadyInstalledError(AdapterServiceError):
    code = "E_FORGE_ADAPTER_ALREADY_INSTALLED"


class AdapterInstallationRequiredError(AdapterServiceError):
    code = "E_FORGE_ADAPTER_NOT_INSTALLED"


class InvalidAdapterInstallationError(AdapterServiceError):
    code = "E_FORGE_ADAPTER_INSTALLATION_INVALID"


class AdapterDriftError(AdapterServiceError):
    code = "E_FORGE_ADAPTER_DRIFT"


class AdapterPlanConflictError(AdapterServiceError):
    code = "E_FORGE_ADAPTER_CONFLICT"


class AdapterTargetUnavailableError(AdapterServiceError):
    code = "E_FORGE_ADAPTER_TARGET_UNAVAILABLE"


@dataclass(frozen=True)
class AdapterPlanResult:
    plan: AdapterPlan
    target: str
    target_source: str
    installed_version: str | None
    current_version: str


@dataclass(frozen=True)
class AdapterMutationResult(AdapterPlanResult):
    mutated: bool


@dataclass(frozen=True)
class _PreparedAdapterPlan:
    driver: HarnessDriver
    record: AdapterInstallationRecord | None
    result: AdapterPlanResult


class AdapterService:
    def __init__(self, registry: AdapterRegistry) -> None:
        self._registry = registry

    def plan(
        self,
        project_root: Path,
        adapter_id: str,
        explicit_target: str | None = None,
    ) -> AdapterPlanResult:
        return self._prepare(project_root, adapter_id, explicit_target).result

    def install(
        self,
        project_root: Path,
        adapter_id: str,
        explicit_target: str | None = None,
        dry_run: bool = False,
    ) -> AdapterMutationResult:
        prepared = self._prepare(project_root, adapter_id, explicit_target)
        if dry_run:
            return self._mutation_result(prepared.result, mutated=False)

        if prepared.record is not None:
            self._require_valid_identity(prepared.record, prepared.driver)
            if prepared.record.adapter_version != prepared.result.current_version:
                raise AdapterAlreadyInstalledError(
                    "Adapter is already installed at a different version; use update."
                )
            self._reject_drift(prepared)
            if self._entirely_unchanged(prepared.result.plan):
                return self._mutation_result(prepared.result, mutated=False)
            raise AdapterAlreadyInstalledError(
                "Adapter is already installed; use update for a changed projection."
            )

        self._reject_conflicts(prepared.result.plan)
        publish_adapter_plan(
            project_root,
            prepared.result.plan,
            self._installation_record(prepared.driver, prepared.result.plan),
        )
        return self._mutation_result(prepared.result, mutated=True)

    def update(
        self,
        project_root: Path,
        adapter_id: str,
        explicit_target: str | None = None,
        dry_run: bool = False,
    ) -> AdapterMutationResult:
        prepared = self._prepare(project_root, adapter_id, explicit_target)
        if prepared.record is None:
            raise AdapterInstallationRequiredError(
                "Adapter update requires an existing installation record."
            )
        self._require_valid_identity(prepared.record, prepared.driver)
        self._reject_drift(prepared)
        self._reject_conflicts(prepared.result.plan)
        if dry_run or (
            self._entirely_unchanged(prepared.result.plan)
            and prepared.record.adapter_version == prepared.result.current_version
        ):
            return self._mutation_result(prepared.result, mutated=False)

        publish_adapter_plan(
            project_root,
            prepared.result.plan,
            self._installation_record(prepared.driver, prepared.result.plan),
        )
        return self._mutation_result(prepared.result, mutated=True)

    def _prepare(
        self,
        project_root: Path,
        adapter_id: str,
        explicit_target: str | None,
    ) -> _PreparedAdapterPlan:
        root = Path(project_root)
        driver = self._registry.get(adapter_id)
        manifest = driver.manifest
        configuration = load_project_configuration(root / ".forge" / "forge.yml")
        target, target_source = self._resolve_target(
            adapter_id=adapter_id,
            explicit_target=explicit_target,
            configuration=load_adapter_configuration(root, adapter_id),
            driver=driver,
        )
        projection = driver.project(
            AdapterProjectionContext(
                project_protocol=configuration["forge"]["protocol"],
                flows=self._effective_flows(root),
                contract_content=resolve_effective_contract(resolve_protocol_root(), root).text,
                target=target,
            )
        )

        try:
            record = load_optional_installation_record(root, adapter_id)
        except InvalidAdapterRepositoryRecordError as error:
            raise InvalidAdapterInstallationError(str(error)) from error
        if record is not None:
            self._require_valid_identity(record, driver)

        desired_paths = {artifact.path for artifact in projection.artifacts}
        recorded_paths = (
            {artifact.path for artifact in record.generated_artifacts}
            if record is not None
            else set()
        )
        try:
            snapshot = snapshot_repository_artifacts(root, desired_paths | recorded_paths)
        except InvalidAdapterRepositoryRecordError as error:
            raise InvalidAdapterInstallationError(str(error)) from error
        except AdapterRepositoryError as error:
            if record is not None:
                raise InvalidAdapterInstallationError(
                    f"Adapter installation record contains unsafe generated state: {error}"
                ) from error
            raise

        expected_digests = (
            {artifact.path: artifact.digest for artifact in record.generated_artifacts}
            if record is not None
            else {}
        )
        states = tuple(
            RepositoryArtifactState(
                path=state.path,
                exists=state.exists,
                current_digest=state.current_digest,
                expected_digest=expected_digests.get(state.path),
            )
            for state in snapshot.artifacts.values()
        )
        plan = plan_adapter(
            manifest=manifest,
            effective_configuration=EffectiveAdapterConfiguration(
                project_protocol=configuration["forge"]["protocol"],
                capability_requirements=(),
            ),
            projections=projection.artifacts,
            repository_state=states,
            additional_limitations=projection.limitations,
            previous_generated=record.generated_artifacts if record is not None else (),
        )
        return _PreparedAdapterPlan(
            driver=driver,
            record=record,
            result=AdapterPlanResult(
                plan=plan,
                target=target,
                target_source=target_source,
                installed_version=record.adapter_version if record is not None else None,
                current_version=manifest.version,
            ),
        )

    @staticmethod
    def _resolve_target(
        *,
        adapter_id: str,
        explicit_target: str | None,
        configuration: AdapterConfiguration | None,
        driver: HarnessDriver,
    ) -> tuple[str, str]:
        if explicit_target is not None:
            return AdapterConfiguration(adapter_id=adapter_id, target=explicit_target).target or "", "explicit"
        if configuration is not None and configuration.target is not None:
            return configuration.target, "configuration"
        if driver.default_target is None:
            raise AdapterTargetUnavailableError("Adapter has no packaged publication target.")
        return AdapterConfiguration(adapter_id=adapter_id, target=driver.default_target).target or "", "evidence"

    @staticmethod
    def _effective_flows(project_root: Path) -> tuple[tuple[str, str], ...]:
        protocol_root = resolve_protocol_root()
        flow_directory = project_root / ".forge" / "flows"
        flows: dict[str, str] = {}
        for path in sorted(flow_directory.glob("*.yml")):
            effective = resolve_effective_flow(protocol_root, project_root, path.stem)
            if effective["project"]["flow"].get("enabled") is not True:
                continue
            canonical = effective["canonical"]
            canonical_id = canonical["flow"]["id"]
            if canonical_id in flows:
                raise AdapterServiceError(f"Duplicate enabled canonical Flow: {canonical_id}.")
            flows[canonical_id] = yaml.safe_dump(canonical, sort_keys=False, allow_unicode=True)
        return tuple(sorted(flows.items()))

    @staticmethod
    def _require_valid_identity(record: AdapterInstallationRecord, driver: HarnessDriver) -> None:
        manifest = driver.manifest
        if record.adapter_id != manifest.adapter_id or record.harness != manifest.harness:
            raise InvalidAdapterInstallationError(
                "Adapter installation record identity does not match the selected Adapter."
            )
        paths = tuple(artifact.path for artifact in record.generated_artifacts)
        if len(paths) != len(set(paths)):
            raise InvalidAdapterInstallationError(
                "Adapter installation record contains duplicate generated artifact paths."
            )

    @staticmethod
    def _reject_conflicts(plan: AdapterPlan) -> None:
        if plan.conflicts:
            raise AdapterPlanConflictError("Adapter plan contains unresolved conflicts.")

    @staticmethod
    def _entirely_unchanged(plan: AdapterPlan) -> bool:
        return all(operation.intent is OperationIntent.UNCHANGED for operation in plan.operations)

    @staticmethod
    def _installation_record(driver: HarnessDriver, plan: AdapterPlan) -> AdapterInstallationRecord:
        manifest = driver.manifest
        generated = (
            GeneratedArtifact(path=operation.path, digest=operation.content_digest)
            for operation in plan.operations
            if operation.ownership is OwnershipMode.FORGE_OWNED
            and operation.intent
            in {OperationIntent.CREATE, OperationIntent.UPDATE, OperationIntent.UNCHANGED}
        )
        return AdapterInstallationRecord(
            adapter_id=manifest.adapter_id,
            adapter_version=manifest.version,
            harness=manifest.harness,
            protocol_min=manifest.protocol_min,
            protocol_max_exclusive=manifest.protocol_max_exclusive,
            generated_artifacts=generated,
            limitations=plan.limitations,
        )

    @staticmethod
    def _mutation_result(result: AdapterPlanResult, *, mutated: bool) -> AdapterMutationResult:
        return AdapterMutationResult(
            plan=result.plan,
            target=result.target,
            target_source=result.target_source,
            installed_version=result.installed_version,
            current_version=result.current_version,
            mutated=mutated,
        )

    @staticmethod
    def _reject_drift(prepared: _PreparedAdapterPlan) -> None:
        assert prepared.record is not None
        recorded_paths = {artifact.path for artifact in prepared.record.generated_artifacts}
        observed = {
            operation.path: operation.expected_current_digest
            for operation in prepared.result.plan.operations
            if operation.path in recorded_paths
            and operation.expected_current_digest is not None
        }
        findings = detect_generated_drift(prepared.record, observed)
        if findings:
            paths = ", ".join(finding.path for finding in findings)
            raise AdapterDriftError(f"Adapter generated artifacts have drifted: {paths}.")
