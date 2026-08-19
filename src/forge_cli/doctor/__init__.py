"""Forge Doctor diagnostics boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from forge_cli.adapters.packaged import build_packaged_registry
from forge_cli.adapters.repository import load_optional_installation_record
from forge_cli.adapters.service import AdapterService
from forge_cli.configuration import (
    InvalidProjectConfigurationError,
    UnsupportedProtocolVersionError,
    load_project_configuration,
)
from forge_cli.git import NotGitRepositoryError, resolve_project_root
from forge_cli.protocol_resolution import (
    CanonicalContractUnavailableError,
    resolve_effective_contract,
)


@dataclass(frozen=True)
class DoctorCheck:
    id: str
    status: str
    message: str


@dataclass(frozen=True)
class DoctorResult:
    checks: tuple[DoctorCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.status != "failed" for check in self.checks)


def _check(check_id: str, status: str, message: str) -> DoctorCheck:
    return DoctorCheck(id=check_id, status=status, message=message)


def diagnose(start: Path, protocol_root: Path) -> DoctorResult:
    """Run read-only Forge environment and project diagnostics."""

    checks: list[DoctorCheck] = []

    if shutil.which("git") is None:
        checks.append(_check("git_available", "failed", "Git executable is unavailable."))
        repository_root: Path | None = None
        checks.append(_check("git_repository", "skipped", "Git repository detection requires Git."))
    else:
        checks.append(_check("git_available", "passed", "Git executable is available."))
        try:
            repository_root = resolve_project_root(start)
        except NotGitRepositoryError:
            repository_root = None
            checks.append(_check("git_repository", "failed", "Current path is not inside a Git repository."))
        else:
            checks.append(_check("git_repository", "passed", f"Git repository detected at {repository_root}."))

    forge_dir = repository_root / ".forge" if repository_root is not None else None
    initialized = forge_dir is not None and forge_dir.is_dir()

    if repository_root is None:
        checks.append(_check("forge_initialized", "skipped", "Forge initialization requires a Git repository."))
    elif not initialized:
        checks.append(_check("forge_initialized", "failed", "Forge is not initialized in this repository."))
    else:
        checks.append(_check("forge_initialized", "passed", "Forge workspace is present."))

    config_valid = False
    protocol_compatible = False
    protocol_id = 1
    if not initialized:
        checks.append(_check("project_configuration", "skipped", "Project configuration requires an initialized Forge workspace."))
        checks.append(_check("protocol_compatibility", "skipped", "Protocol compatibility requires valid project configuration."))
        checks.append(_check("canonical_flows", "skipped", "Canonical Flow checks require an initialized Forge workspace."))
    else:
        config_path = forge_dir / "forge.yml"
        try:
            project_configuration = load_project_configuration(config_path)
        except UnsupportedProtocolVersionError as error:
            config_valid = True
            checks.append(_check("project_configuration", "passed", "Project configuration conforms to the Forge Project Schema."))
            checks.append(_check("protocol_compatibility", "failed", str(error)))
        except InvalidProjectConfigurationError as error:
            checks.append(_check("project_configuration", "failed", str(error)))
            checks.append(_check("protocol_compatibility", "skipped", "Protocol compatibility requires valid project configuration."))
        else:
            config_valid = True
            protocol_compatible = True
            protocol_id = project_configuration["forge"]["protocol"]
            checks.append(_check("project_configuration", "passed", "Project configuration conforms to the Forge Project Schema."))
            checks.append(_check("protocol_compatibility", "passed", f"Configured Forge Protocol {protocol_id} is supported."))

        canonical_flow_ids = ("fast", "standard", "full")
        if config_valid and protocol_compatible:
            missing = [
                flow_id
                for flow_id in canonical_flow_ids
                if not (protocol_root / "flows" / f"{flow_id}.yml").is_file()
            ]
            if missing:
                checks.append(
                    _check(
                        "canonical_flows",
                        "failed",
                        f"Canonical Forge Flows are unavailable: {', '.join(missing)}.",
                    )
                )
            else:
                checks.append(_check("canonical_flows", "passed", "FAST, STANDARD, and FULL canonical Flows are available."))
        else:
            checks.append(_check("canonical_flows", "skipped", "Canonical Flow checks require compatible project configuration."))

    contract_project_root = repository_root if repository_root is not None else start

    try:
        resolve_effective_contract(protocol_root, contract_project_root, protocol_id)
    except CanonicalContractUnavailableError as error:
        checks.append(_check("canonical_contract", "failed", str(error)))
    else:
        checks.append(_check("canonical_contract", "passed", f"Canonical Protocol {protocol_id} Engineering Contract is available."))

    if initialized:
        checks.extend(_adapter_readiness_checks(repository_root))

    return DoctorResult(checks=tuple(checks))


def _adapter_readiness_checks(repository_root: Path) -> list[DoctorCheck]:
    """Aggregate every installed Adapter's own diagnostics into readiness checks."""
    registry = build_packaged_registry()
    service = AdapterService(registry)
    checks: list[DoctorCheck] = []
    for driver in registry.list():
        adapter_id = driver.manifest.adapter_id
        if load_optional_installation_record(repository_root, adapter_id) is None:
            continue
        result = service.doctor(repository_root, adapter_id)
        status_map = {"passed": "passed", "failed": "failed", "warning": "passed"}
        for check in result.checks:
            checks.append(
                _check(
                    f"adapter:{adapter_id}:{check.id}",
                    status_map[check.status],
                    check.message,
                )
            )
    return checks
