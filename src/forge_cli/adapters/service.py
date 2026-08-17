"""Generic Adapter use-case orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from forge_cli.adapters.configuration import (
    AdapterConfiguration,
    InvalidAdapterConfigurationError,
    load_adapter_configuration,
)
from forge_cli.adapters.diagnostics import (
    AdapterCheck,
    AdapterDoctorResult,
    AdapterValidationResult,
    diagnose_adapter,
    validate_adapter,
)
from forge_cli.adapters.driver import AdapterProjectionContext, HarnessDriver
from forge_cli.adapters.manifest import is_protocol_compatible
from forge_cli.adapters.ownership import (
    InvalidAdapterPublicationOwnershipError,
    detect_generated_drift,
    require_publication_root_ownership,
    require_recorded_publication_ownership,
)
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
from forge_cli.configuration import (
    InvalidProjectConfigurationError,
    UnsupportedProtocolVersionError,
    load_project_configuration,
)
from forge_cli.protocol_resources import resolve_protocol_root
from forge_cli.protocol_resolution import (
    ProtocolResolutionError,
    resolve_effective_contract,
    resolve_effective_flow,
)
from forge_cli.adapters.validation import ConformanceRequirements, validate_conformance


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


class AdapterFlowConfigurationError(AdapterServiceError):
    code = "E_FORGE_ADAPTER_FLOW_CONFIGURATION"


def require_valid_installation_identity(
    record: AdapterInstallationRecord,
    driver: HarnessDriver,
) -> None:
    """Reject installation state that cannot belong to the selected Adapter."""
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
    try:
        require_recorded_publication_ownership(record)
        assert record.publication_root is not None
        driver.validate_publication_root(record.publication_root)
    except (InvalidAdapterPublicationOwnershipError, TypeError, ValueError) as error:
        raise InvalidAdapterInstallationError(
            f"Adapter installation record has invalid publication ownership: {error}"
        ) from error


def _passed_check(check_id: str, message: str) -> AdapterCheck:
    return AdapterCheck(id=check_id, status="passed", code="OK", message=message)


def _failed_check(
    check_id: str,
    code: str,
    message: str,
    remediation: str,
) -> AdapterCheck:
    return AdapterCheck(
        id=check_id,
        status="failed",
        code=code,
        message=message,
        remediation=remediation,
    )


def _warning_check(check_id: str, code: str, message: str) -> AdapterCheck:
    return AdapterCheck(id=check_id, status="warning", code=code, message=message)


def _conformance_requirements(
    flows: tuple[tuple[str, str], ...],
) -> ConformanceRequirements:
    stages: set[str] = set()
    gates: set[str] = set()
    tdd_red_required = False
    strict_review_required = False

    for _, content in flows:
        data = yaml.safe_load(content) or {}
        for stage in data.get("stages") or ():
            if isinstance(stage, dict) and isinstance(stage.get("id"), str):
                stages.add(stage["id"])
        flow_gates = data.get("gates") or {}
        if isinstance(flow_gates, dict):
            gates.update(str(gate) for gate in flow_gates)
            behavioral = flow_gates.get("before_behavioral_implementation") or {}
            checks = behavioral.get("checks") if isinstance(behavioral, dict) else ()
            tdd_red_required = tdd_red_required or {
                "red_executed",
                "red_failed_for_expected_reason",
            }.issubset(checks or ())
        review = data.get("review") or {}
        strict_review_required = strict_review_required or (
            "strict_review" in stages
            or (isinstance(review, dict) and review.get("strict") is True)
        )

    invariants: list[str] = []
    if tdd_red_required:
        invariants.append("tdd-red-before-behavior")
    if strict_review_required:
        invariants.append("strict-review")
    return ConformanceRequirements(
        required_stages=tuple(sorted(stages)),
        required_gates=tuple(sorted(gates)),
        required_invariants=tuple(invariants),
        tdd_red_required=tdd_red_required,
        strict_review_required=strict_review_required,
    )


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

    def validate(
        self,
        project_root: Path,
        adapter_id: str,
        explicit_target: str | None = None,
    ) -> AdapterValidationResult:
        """Read the Adapter state and return failures suitable for CLI serialization."""
        return validate_adapter(self.doctor(project_root, adapter_id, explicit_target))

    def doctor(
        self,
        project_root: Path,
        adapter_id: str,
        explicit_target: str | None = None,
    ) -> AdapterDoctorResult:
        """Diagnose Adapter state without creating, normalizing, or publishing files."""
        root = Path(project_root)
        driver = self._registry.get(adapter_id)
        manifest = driver.manifest
        checks: list[AdapterCheck] = []

        configuration: AdapterConfiguration | None = None
        project_configuration: dict | None = None
        project_protocol: int | None = None
        configuration_failure: AdapterCheck | None = None
        try:
            project_configuration = load_project_configuration(root / ".forge" / "forge.yml")
            project_protocol = project_configuration["forge"]["protocol"]
        except UnsupportedProtocolVersionError as error:
            configuration_failure = _failed_check(
                "configuration",
                error.code,
                str(error),
                "Set `.forge/forge.yml` to a supported Forge Protocol, then rerun diagnostics.",
            )
        except InvalidProjectConfigurationError as error:
            configuration_failure = _failed_check(
                "configuration",
                error.code,
                str(error),
                "Repair `.forge/forge.yml` so it satisfies the Forge Project Schema, then rerun diagnostics.",
            )

        try:
            configuration = load_adapter_configuration(root, adapter_id)
        except InvalidAdapterConfigurationError as error:
            if configuration_failure is None:
                configuration_failure = _failed_check(
                    "configuration",
                    error.code,
                    str(error),
                    "Repair `.forge/adapters/<adapter>/config.yml` or remove it to use packaged target evidence.",
                )

        if configuration_failure is not None:
            checks.append(configuration_failure)
        else:
            checks.append(
                _passed_check(
                    "configuration",
                    "Adapter and project configuration are valid.",
                )
            )

        if project_protocol is None:
            checks.append(
                _warning_check(
                    "compatibility",
                    "W_FORGE_ADAPTER_COMPATIBILITY_UNAVAILABLE",
                    "Protocol compatibility cannot be checked until project configuration is valid.",
                )
            )
        elif is_protocol_compatible(manifest, project_protocol):
            checks.append(
                _passed_check(
                    "compatibility",
                    f"Adapter supports configured Forge Protocol {project_protocol}.",
                )
            )
        else:
            checks.append(
                _failed_check(
                    "compatibility",
                    "E_FORGE_ADAPTER_PROTOCOL_INCOMPATIBLE",
                    "Adapter does not support configured Forge Protocol "
                    f"{project_protocol}; supported interval is "
                    f"[{manifest.protocol_min}, {manifest.protocol_max_exclusive}).",
                    "Select an Adapter version compatible with the configured Forge Protocol.",
                )
            )

        target: str | None = None
        try:
            target, _ = self._resolve_target(
                adapter_id=adapter_id,
                explicit_target=explicit_target,
                configuration=configuration,
                driver=driver,
            )
        except (AdapterTargetUnavailableError, InvalidAdapterConfigurationError) as error:
            checks.append(
                _failed_check(
                    "target",
                    getattr(error, "code", "E_FORGE_ADAPTER_TARGET_UNAVAILABLE"),
                    str(error),
                    "Provide a safe repository-relative Adapter target or repair packaged target evidence.",
                )
            )
        else:
            checks.append(
                _passed_check("target", f"Adapter target is `{target}`."))

        record: AdapterInstallationRecord | None = None
        installation_failure: AdapterCheck | None = None
        try:
            candidate_record = load_optional_installation_record(root, adapter_id)
            if candidate_record is None:
                checks.append(
                    _failed_check(
                        "installation",
                        "E_FORGE_ADAPTER_NOT_INSTALLED",
                        "Adapter is not installed.",
                        f"Run `forge adapter install {adapter_id}`.",
                    )
                )
            else:
                require_valid_installation_identity(candidate_record, driver)
                if target is not None and candidate_record.publication_root != target:
                    raise InvalidAdapterInstallationError(
                        "Adapter installation record publication root does not match "
                        "the resolved Adapter target."
                    )
                if candidate_record.adapter_version != manifest.version:
                    checks.append(
                        _failed_check(
                            "installation",
                            "E_FORGE_ADAPTER_INSTALLATION_STALE",
                            "Adapter installation record version does not match the packaged Adapter version.",
                            f"Run `forge adapter update {adapter_id}` to refresh the installation record.",
                        )
                    )
                else:
                    checks.append(
                        _passed_check("installation", "Adapter installation record is valid and current.")
                    )
                record = candidate_record
        except (AdapterRepositoryError, InvalidAdapterInstallationError) as error:
            installation_failure = _failed_check(
                "installation",
                "E_FORGE_ADAPTER_INSTALLATION_INVALID",
                f"Adapter installation state is invalid: {error}",
                f"Repair or remove the invalid installation record, then run `forge adapter install {adapter_id}`.",
            )
            checks.append(installation_failure)

        if record is None:
            if installation_failure is None:
                checks.append(
                    _warning_check(
                        "generated_drift",
                        "W_FORGE_ADAPTER_DRIFT_UNAVAILABLE",
                        "Generated drift cannot be checked until a valid installation record is available.",
                    )
                )
            else:
                checks.append(
                    _failed_check(
                        "generated_drift",
                        "E_FORGE_ADAPTER_INSTALLATION_INVALID",
                        "Unsafe recorded generated paths cannot be read safely: "
                        f"{installation_failure.message}",
                        f"Repair or remove the invalid installation record, then run `forge adapter install {adapter_id}`.",
                    )
                )
        else:
            try:
                snapshot = snapshot_repository_artifacts(
                    root,
                    (artifact.path for artifact in record.generated_artifacts),
                )
            except AdapterRepositoryError as error:
                checks.append(
                    _failed_check(
                        "generated_drift",
                        "E_FORGE_ADAPTER_INSTALLATION_INVALID",
                        f"Unsafe recorded generated paths cannot be read safely: {error}",
                        f"Repair or remove the invalid installation record, then run `forge adapter install {adapter_id}`.",
                    )
                )
            else:
                observed = {
                    path: state.current_digest for path, state in snapshot.artifacts.items()
                }
                drift = detect_generated_drift(record, observed)
                if not drift:
                    checks.append(
                        _passed_check("generated_drift", "Recorded generated artifacts are intact."))
                else:
                    description = ", ".join(
                        f"{item.kind}: {item.path}" for item in drift
                    )
                    checks.append(
                        _failed_check(
                            "generated_drift",
                            "E_FORGE_ADAPTER_DRIFT",
                            f"Generated artifacts have drifted ({description}).",
                            "restore the recorded artifact from trusted generated content, then rerun `forge adapter validate`.",
                        )
                    )

        projection = None
        if project_configuration is None or target is None:
            checks.append(
                _warning_check(
                    "conformance",
                    "W_FORGE_ADAPTER_CONFORMANCE_UNAVAILABLE",
                    "Adapter conformance cannot be checked until project configuration and target are valid.",
                )
            )
        else:
            try:
                protocol_id = project_configuration["forge"]["protocol"]
                flows = self._effective_flows(root, protocol_id)
                projection = driver.project(
                    AdapterProjectionContext(
                        project_protocol=protocol_id,
                        flows=flows,
                        contract_content=resolve_effective_contract(
                            resolve_protocol_root(), root, protocol_id
                        ).text,
                        target=target,
                    )
                )
            except (AdapterServiceError, ProtocolResolutionError) as error:
                checks.append(
                    _failed_check(
                        "conformance",
                        "E_FORGE_ADAPTER_CONFORMANCE",
                        f"Adapter conformance inputs are invalid: {error}",
                        "Repair the effective Forge Flow or Contract input, then rerun diagnostics.",
                    )
                )
            else:
                findings = validate_conformance(
                    _conformance_requirements(flows), projection.representation
                )
                if findings:
                    labels = ", ".join(
                        f"{finding.code}{f': {finding.subject}' if finding.subject else ''}"
                        for finding in findings
                    )
                    checks.append(
                        _failed_check(
                            "conformance",
                            "E_FORGE_ADAPTER_CONFORMANCE",
                            f"Adapter representation does not preserve required Forge semantics ({labels}).",
                            "Update the Adapter representation to preserve the reported Forge semantics, then rerun validation.",
                        )
                    )
                else:
                    checks.append(
                        _passed_check(
                            "conformance",
                            "Adapter representation preserves the checked Forge semantics.",
                        )
                    )

        if projection is None:
            checks.append(
                _warning_check(
                    "limitations",
                    "W_FORGE_ADAPTER_LIMITATIONS_UNAVAILABLE",
                    "Adapter capability limitations cannot be inspected until representation is available.",
                )
            )
        elif not projection.limitations:
            checks.append(_passed_check("limitations", "No Adapter capability limitations are reported."))
        else:
            details = "; ".join(
                f"{item.requirement_id} uses {item.capability} ({item.source_reference})"
                for item in sorted(
                    projection.limitations,
                    key=lambda item: (
                        item.requirement_id,
                        item.capability,
                        item.source_reference,
                    ),
                )
            )
            checks.append(
                _warning_check(
                    "limitations",
                    "W_FORGE_ADAPTER_LIMITATION",
                    f"Adapter capability limitations are represented: {details}.",
                )
            )

        return diagnose_adapter(checks)

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
            require_valid_installation_identity(prepared.record, prepared.driver)
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
            self._installation_record(
                prepared.driver,
                prepared.result.plan,
                prepared.result.target,
            ),
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
        require_valid_installation_identity(prepared.record, prepared.driver)
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
            self._installation_record(
                prepared.driver,
                prepared.result.plan,
                prepared.result.target,
            ),
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
        protocol_id = configuration["forge"]["protocol"]
        projection = driver.project(
            AdapterProjectionContext(
                project_protocol=protocol_id,
                flows=self._effective_flows(root, protocol_id),
                contract_content=resolve_effective_contract(
                    resolve_protocol_root(), root, protocol_id
                ).text,
                target=target,
            )
        )
        try:
            require_publication_root_ownership(
                target,
                (artifact.path for artifact in projection.artifacts),
            )
        except InvalidAdapterPublicationOwnershipError as error:
            raise AdapterServiceError(
                f"Adapter projection violates its publication root: {error}"
            ) from error

        try:
            record = load_optional_installation_record(root, adapter_id)
        except InvalidAdapterRepositoryRecordError as error:
            raise InvalidAdapterInstallationError(str(error)) from error
        if record is not None:
            require_valid_installation_identity(record, driver)
            if record.publication_root != target:
                raise InvalidAdapterInstallationError(
                    "Adapter installation record publication root does not match "
                    "the resolved Adapter target."
                )

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
            target = AdapterConfiguration(
                adapter_id=adapter_id,
                target=explicit_target,
            ).target or ""
            source = "explicit"
        elif configuration is not None and configuration.target is not None:
            target = configuration.target
            source = "configuration"
        else:
            if driver.default_target is None:
                raise AdapterTargetUnavailableError(
                    "Adapter has no packaged publication target."
                )
            target = AdapterConfiguration(
                adapter_id=adapter_id,
                target=driver.default_target,
            ).target or ""
            source = "evidence"

        try:
            driver.validate_publication_root(target)
            require_publication_root_ownership(target, ())
        except (TypeError, ValueError) as error:
            raise InvalidAdapterConfigurationError(
                f"Adapter publication target is invalid for its Harness: {target!r}."
            ) from error
        return target, source

    @staticmethod
    def _effective_flows(project_root: Path, protocol_id: int = 1) -> tuple[tuple[str, str], ...]:
        protocol_root = resolve_protocol_root()
        flow_directory = project_root / ".forge" / "flows"
        flows: dict[str, str] = {}
        for path in sorted(flow_directory.glob("*.yml")):
            effective = resolve_effective_flow(protocol_root, project_root, path.stem, protocol_id)
            if effective["project"]["flow"].get("enabled") is not True:
                continue
            canonical = effective["canonical"]
            canonical_id = canonical["flow"]["id"]
            if canonical_id in flows:
                raise AdapterFlowConfigurationError(
                    f"Duplicate enabled canonical Flow: {canonical_id}."
                )
            flows[canonical_id] = yaml.safe_dump(canonical, sort_keys=False, allow_unicode=True)
        return tuple(sorted(flows.items()))

    @staticmethod
    def _reject_conflicts(plan: AdapterPlan) -> None:
        if plan.conflicts:
            raise AdapterPlanConflictError("Adapter plan contains unresolved conflicts.")

    @staticmethod
    def _entirely_unchanged(plan: AdapterPlan) -> bool:
        return all(operation.intent is OperationIntent.UNCHANGED for operation in plan.operations)

    @staticmethod
    def _installation_record(
        driver: HarnessDriver,
        plan: AdapterPlan,
        publication_root: str,
    ) -> AdapterInstallationRecord:
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
            publication_root=publication_root,
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
