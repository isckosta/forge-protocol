"""Forge validation boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

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


def _validate_reviewer_resolver_separation(project_root: Path) -> list[ValidationFinding]:
    """Apply semantic C-026 checks after JSON Schema structural validation.

    Change schemas own presence, closure, types, and non-empty execution/context
    identifiers. This validator owns semantic independence: a Role rename does
    not create independence when the Reviewer shares either the concrete
    Execution or transient Execution Context with the implementation/resolution
    being reviewed.
    """
    findings: list[ValidationFinding] = []
    changes_dir = project_root / ".forge" / "changes"
    if not changes_dir.is_dir():
        return findings

    for manifest_path in sorted(changes_dir.glob("*/manifest.yml")):
        try:
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(manifest, dict):
            continue

        flow = manifest.get("flow") or {}
        review = manifest.get("review") or {}
        identity = review.get("reviewer_identity") or {}
        if not (
            isinstance(flow, dict)
            and flow.get("current") in {"standard", "full"}
            and isinstance(identity, dict)
        ):
            continue

        execution_id = identity.get("execution_id")
        context_id = identity.get("context_id")
        resolver_execution_id = identity.get("resolver_execution_id")
        resolver_context_id = identity.get("resolver_context_id")

        if (
            isinstance(execution_id, str)
            and isinstance(resolver_execution_id, str)
            and execution_id == resolver_execution_id
        ):
            findings.append(
                ValidationFinding(
                    code="C-026",
                    artifact=str(manifest_path.relative_to(project_root)),
                    path=manifest_path,
                    message=(
                        "Strict Review is not independent: reviewer_identity.execution_id "
                        "matches resolver_execution_id. Changing Role inside one Execution "
                        "does not satisfy Reviewer independence."
                    ),
                )
            )

        if (
            isinstance(context_id, str)
            and isinstance(resolver_context_id, str)
            and context_id == resolver_context_id
        ):
            findings.append(
                ValidationFinding(
                    code="C-026",
                    artifact=str(manifest_path.relative_to(project_root)),
                    path=manifest_path,
                    message=(
                        "Strict Review is context-contaminated: reviewer_identity.context_id "
                        "matches resolver_context_id. A distinct Execution ID cannot make a "
                        "shared conversational/reasoning context independent."
                    ),
                )
            )

    return findings


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

    findings.extend(_validate_reviewer_resolver_separation(project_root))

    return ValidationResult(findings=tuple(findings))
