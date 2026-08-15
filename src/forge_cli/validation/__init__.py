"""Forge validation boundary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

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


def _finding(project_root: Path, path: Path, message: str) -> ValidationFinding:
    return ValidationFinding(
        code="C-026",
        artifact=str(path.relative_to(project_root)),
        path=path,
        message=message,
    )


def _load_mapping(path: Path) -> dict[str, Any] | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return None
    return data if isinstance(data, dict) else None


def _record_fields(record: object) -> tuple[str, str, str, str, str] | None:
    if not isinstance(record, dict):
        return None
    record_id = record.get("id")
    role = record.get("role")
    execution = record.get("execution")
    revision = record.get("revision")
    source = record.get("source")
    if not (
        isinstance(record_id, str)
        and record_id
        and role in {"implementation", "resolution", "review"}
        and isinstance(execution, dict)
        and isinstance(revision, dict)
        and isinstance(source, dict)
    ):
        return None
    execution_id = execution.get("id")
    context_id = execution.get("context_id")
    revision_id = revision.get("id")
    assurance = source.get("assurance")
    if not (
        isinstance(execution_id, str)
        and execution_id
        and isinstance(context_id, str)
        and context_id
        and isinstance(revision_id, str)
        and revision_id
        and assurance in {"claimed", "recorded", "verified"}
    ):
        return None
    return record_id, role, execution_id, context_id, revision_id


def _validate_protocol2_review_provenance(project_root: Path) -> list[ValidationFinding]:
    """Validate Protocol 2 C-026 against repository-native provenance records.

    Core verifies durable record linkage, revision binding and boundary consistency.
    It deliberately does not claim that a self-recorded provenance record is a
    cryptographic proof of a real external execution. `verified` provenance is a
    stronger assurance level supplied by an observer such as a Harness Adapter.
    """
    findings: list[ValidationFinding] = []
    changes_dir = project_root / ".forge" / "changes"
    if not changes_dir.is_dir():
        return findings

    for manifest_path in sorted(changes_dir.glob("*/manifest.yml")):
        manifest = _load_mapping(manifest_path)
        if manifest is None:
            continue

        schema_id = manifest.get("schema")
        state = manifest.get("state") or {}
        state_current = state.get("current") if isinstance(state, dict) else None

        # Protocol 2 permits untouched completed Protocol 1 history, but an active
        # Change cannot downgrade its manifest schema to escape Protocol 2 gates.
        if schema_id == "forge/change@1":
            if state_current != "complete":
                findings.append(
                    _finding(
                        project_root,
                        manifest_path,
                        "Protocol 2 active Changes must use forge/change@2; forge/change@1 "
                        "cannot be used to bypass C-026 provenance requirements.",
                    )
                )
            continue

        if schema_id != "forge/change@2":
            continue

        if manifest.get("protocol") != 2:
            findings.append(
                _finding(
                    project_root,
                    manifest_path,
                    "forge/change@2 is a Protocol 2 Change manifest and must declare protocol: 2.",
                )
            )
            continue

        review = manifest.get("review") or {}
        if not isinstance(review, dict) or review.get("status") != "passed":
            continue

        iterations = review.get("iterations")
        if not isinstance(iterations, list) or not iterations:
            findings.append(
                _finding(
                    project_root,
                    manifest_path,
                    "Protocol 2 review_passed requires at least one Review Iteration linked to provenance.",
                )
            )
            continue

        provenance_path = manifest_path.parent / "provenance.yml"
        provenance = _load_mapping(provenance_path)
        if provenance is None:
            findings.append(
                _finding(
                    project_root,
                    manifest_path,
                    "Protocol 2 review_passed requires repository-native provenance.yml evidence.",
                )
            )
            continue

        if provenance.get("schema") != "forge/execution-provenance@1":
            findings.append(
                _finding(
                    project_root,
                    provenance_path,
                    "Protocol 2 review provenance uses an unsupported or missing provenance schema.",
                )
            )
            continue

        records = provenance.get("records")
        if not isinstance(records, list):
            findings.append(
                _finding(project_root, provenance_path, "Protocol 2 provenance records are missing.")
            )
            continue

        record_index: dict[str, dict[str, Any]] = {}
        invalid_record = False
        for record in records:
            fields = _record_fields(record)
            if fields is None:
                invalid_record = True
                break
            record_id = fields[0]
            if record_id in record_index:
                invalid_record = True
                break
            record_index[record_id] = record
        if invalid_record:
            findings.append(
                _finding(
                    project_root,
                    provenance_path,
                    "Protocol 2 provenance contains a partial, duplicate, or structurally incomplete record.",
                )
            )
            continue

        passed_iterations = [
            item for item in iterations
            if isinstance(item, dict) and item.get("status") == "passed"
        ]
        if not passed_iterations:
            findings.append(
                _finding(
                    project_root,
                    manifest_path,
                    "review.status is passed but no Review Iteration is recorded as passed.",
                )
            )
            continue

        for iteration in passed_iterations:
            revision_id = iteration.get("revision")
            subject_ref = iteration.get("subject_provenance")
            reviewer_ref = iteration.get("reviewer_provenance")
            if not all(isinstance(value, str) and value for value in (revision_id, subject_ref, reviewer_ref)):
                findings.append(
                    _finding(
                        project_root,
                        manifest_path,
                        "A passed Protocol 2 Review Iteration requires revision, subject_provenance, and reviewer_provenance references.",
                    )
                )
                continue

            subject = record_index.get(subject_ref)
            reviewer = record_index.get(reviewer_ref)
            if subject is None or reviewer is None:
                findings.append(
                    _finding(
                        project_root,
                        manifest_path,
                        "A passed Review Iteration references provenance that was not found in provenance.yml; distinct invented IDs are not proof of independence.",
                    )
                )
                continue

            subject_fields = _record_fields(subject)
            reviewer_fields = _record_fields(reviewer)
            if subject_fields is None or reviewer_fields is None:
                findings.append(
                    _finding(project_root, provenance_path, "Referenced provenance is structurally incomplete.")
                )
                continue

            _, subject_role, subject_execution, subject_context, subject_revision = subject_fields
            _, reviewer_role, reviewer_execution, reviewer_context, reviewer_revision = reviewer_fields
            subject_assurance = subject["source"].get("assurance")
            reviewer_assurance = reviewer["source"].get("assurance")

            if subject_role not in {"implementation", "resolution"} or reviewer_role != "review":
                findings.append(
                    _finding(
                        project_root,
                        manifest_path,
                        "Review provenance roles are invalid: subject must be implementation/resolution and reviewer must be review.",
                    )
                )
                continue

            if subject_assurance not in {"recorded", "verified"} or reviewer_assurance not in {"recorded", "verified"}:
                findings.append(
                    _finding(
                        project_root,
                        manifest_path,
                        "review_passed requires recorded or verified provenance; claimed identity alone is insufficient.",
                    )
                )
                continue

            if subject_revision != revision_id or reviewer_revision != revision_id:
                findings.append(
                    _finding(
                        project_root,
                        manifest_path,
                        "Review provenance does not bind both executions to the revision under review.",
                    )
                )

            if subject_execution == reviewer_execution:
                findings.append(
                    _finding(
                        project_root,
                        manifest_path,
                        "Strict Review is not independent: Reviewer and subject provenance share the same Execution.",
                    )
                )

            if subject_context == reviewer_context:
                findings.append(
                    _finding(
                        project_root,
                        manifest_path,
                        "Strict Review is context-contaminated: Reviewer and subject provenance share the same Execution Context.",
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
        project_configuration = load_project_configuration(config_path)
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

    protocol_id = project_configuration["forge"]["protocol"]
    findings: list[ValidationFinding] = []

    flow_dir = forge_dir / "flows"
    if flow_dir.is_dir():
        for flow_path in sorted(flow_dir.glob("*.yml")):
            try:
                resolve_effective_flow(protocol_root, project_root, flow_path.stem, protocol_id)
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
        resolve_effective_contract(protocol_root, project_root, protocol_id)
    except CanonicalContractUnavailableError as error:
        findings.append(
            ValidationFinding(
                code="E_FORGE_CANONICAL_CONTRACT_UNAVAILABLE",
                artifact=f"protocol/{protocol_id}/contract/engineering.md",
                path=protocol_root,
                message=str(error),
            )
        )

    if protocol_id == 2:
        findings.extend(_validate_protocol2_review_provenance(project_root))

    return ValidationResult(findings=tuple(findings))
