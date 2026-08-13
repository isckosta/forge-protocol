"""Forge validation boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from forge_cli.configuration import (
    InvalidProjectConfigurationError,
    UnsupportedProtocolVersionError,
    load_project_configuration,
)
from forge_cli.protocol_resolution import (
    CanonicalContractUnavailableError,
    InvalidProjectFlowConfigurationError,
    UnknownCanonicalFlowError,
    resolve_effective_contract,
    resolve_effective_flow,
)


@dataclass(frozen=True)
class ValidationFinding:
    code: str
    artifact: str
    message: str
    path: Path | None = None


@dataclass(frozen=True)
class ValidationResult:
    findings: tuple[ValidationFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


def validate_project(project_root: Path, protocol_root: Path) -> ValidationResult:
    forge_dir = project_root / ".forge"
    if not forge_dir.is_dir():
        return ValidationResult(
            findings=(
                ValidationFinding(
                    code="E_FORGE_NOT_INITIALIZED",
                    artifact=".forge/",
                    path=forge_dir,
                    message="Forge is not initialized. Run `forge init` from this Git repository.",
                ),
            )
        )

    config_path = forge_dir / "forge.yml"
    try:
        load_project_configuration(config_path)
    except UnsupportedProtocolVersionError as error:
        return ValidationResult(
            findings=(
                ValidationFinding(
                    code=error.code,
                    artifact=".forge/forge.yml",
                    path=config_path,
                    message=str(error),
                ),
            )
        )
    except InvalidProjectConfigurationError as error:
        return ValidationResult(
            findings=(
                ValidationFinding(
                    code=error.code,
                    artifact=".forge/forge.yml",
                    path=config_path,
                    message=str(error),
                ),
            )
        )

    findings: list[ValidationFinding] = []

    flow_dir = forge_dir / "flows"
    if flow_dir.is_dir():
        for flow_path in sorted(flow_dir.glob("*.yml")):
            try:
                resolve_effective_flow(protocol_root, project_root, flow_path.stem)
            except UnknownCanonicalFlowError as error:
                findings.append(
                    ValidationFinding(
                        code="E_FORGE_UNKNOWN_CANONICAL_FLOW",
                        artifact=str(flow_path.relative_to(project_root)),
                        path=flow_path,
                        message=str(error),
                    )
                )
            except InvalidProjectFlowConfigurationError as error:
                findings.append(
                    ValidationFinding(
                        code="E_FORGE_INVALID_PROJECT_FLOW",
                        artifact=str(flow_path.relative_to(project_root)),
                        path=flow_path,
                        message=str(error),
                    )
                )

    try:
        resolve_effective_contract(protocol_root, project_root)
    except CanonicalContractUnavailableError as error:
        findings.append(
            ValidationFinding(
                code="E_FORGE_CANONICAL_CONTRACT_UNAVAILABLE",
                artifact="protocol/contract/engineering.md",
                path=protocol_root / "contract" / "engineering.md",
                message=str(error),
            )
        )

    return ValidationResult(findings=tuple(findings))
