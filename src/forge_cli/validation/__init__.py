"""Forge validation boundary."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any
import yaml
from forge_cli.configuration import InvalidProjectConfigurationError, UnsupportedProtocolVersionError, load_project_configuration
from forge_cli.protocol_resolution import CanonicalContractUnavailableError, InvalidProjectFlowConfigurationError, UnknownCanonicalFlowError, resolve_effective_contract, resolve_effective_flow

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

def _finding(root: Path, path: Path, message: str) -> ValidationFinding:
    return ValidationFinding("C-026", str(path.relative_to(root)), message, path)

def _load_mapping(path: Path) -> dict[str, Any] | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return None
    return data if isinstance(data, dict) else None

def _record_fields(record: object) -> tuple[str, str, str, str, str, tuple[str, str]] | None:
    if not isinstance(record, dict):
        return None
    execution, revision, source = record.get("execution"), record.get("revision"), record.get("source")
    record_id, role = record.get("id"), record.get("role")
    if not (isinstance(record_id, str) and record_id and role in {"implementation", "resolution", "review"} and isinstance(execution, dict) and isinstance(revision, dict) and isinstance(source, dict)):
        return None
    execution_id, context_id, revision_id = execution.get("id"), execution.get("context_id"), revision.get("id")
    if not (isinstance(execution_id, str) and execution_id and isinstance(context_id, str) and context_id and isinstance(revision_id, str) and revision_id and source.get("assurance") in {"claimed", "recorded", "verified"}):
        return None
    immutable = revision.get("immutable_ref")
    commit = revision.get("commit")
    if immutable is None and isinstance(commit, str):
        immutable = {"type": "git_commit", "value": commit}
    if not isinstance(immutable, dict):
        return None
    ref_type, ref_value = immutable.get("type"), immutable.get("value")
    if ref_type not in {"git_commit", "content_digest", "vcs_revision"} or not isinstance(ref_value, str) or not ref_value:
        return None
    if ref_type == "git_commit":
        if len(ref_value) != 40 or any(c not in "0123456789abcdefABCDEF" for c in ref_value):
            return None
        ref_value = ref_value.lower()
    if commit is not None and (ref_type != "git_commit" or not isinstance(commit, str) or commit.lower() != ref_value):
        return None
    return record_id, role, execution_id, context_id, revision_id, (ref_type, ref_value)

def _git_commit_exists(root: Path, commit: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=root, capture_output=True, check=False).returncode == 0

def _subject_changed_after_freeze(root: Path, manifest_path: Path, commit: str) -> bool:
    result = subprocess.run(["git", "diff", "--name-only", f"{commit}..HEAD"], cwd=root, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return True
    change_dir = manifest_path.parent.relative_to(root).as_posix()
    allowed = {f"{change_dir}/manifest.yml", f"{change_dir}/provenance.yml", f"{change_dir}/review.md"}
    return bool({line.strip() for line in result.stdout.splitlines() if line.strip()} - allowed)

def _validate_protocol2_review_provenance(root: Path) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    changes = root / ".forge" / "changes"
    if not changes.is_dir():
        return findings
    for manifest_path in sorted(changes.glob("*/manifest.yml")):
        manifest = _load_mapping(manifest_path)
        if manifest is None:
            continue
        state = manifest.get("state") or {}
        if manifest.get("schema") == "forge/change@1":
            if not isinstance(state, dict) or state.get("current") != "complete":
                findings.append(_finding(root, manifest_path, "Protocol 2 active Changes must use forge/change@2; forge/change@1 cannot bypass C-026."))
            continue
        if manifest.get("schema") != "forge/change@2":
            continue
        if manifest.get("protocol") != 2:
            findings.append(_finding(root, manifest_path, "forge/change@2 must declare protocol: 2.")); continue
        review = manifest.get("review") or {}
        if not isinstance(review, dict):
            continue
        iterations = review.get("iterations")
        if not isinstance(iterations, list) or not iterations:
            if review.get("status") == "passed":
                findings.append(_finding(root, manifest_path, "Protocol 2 review_passed requires a Review Iteration linked to provenance."))
            continue
        bound = [i for i in iterations if isinstance(i, dict) and i.get("subject_provenance")]
        if not bound and review.get("status") != "passed":
            continue
        provenance_path = manifest_path.parent / "provenance.yml"
        provenance = _load_mapping(provenance_path)
        if provenance is None or provenance.get("schema") != "forge/execution-provenance@1":
            findings.append(_finding(root, provenance_path if provenance_path.exists() else manifest_path, "Protocol 2 bound Review Iterations require supported repository-native provenance.")); continue
        records = provenance.get("records")
        if not isinstance(records, list):
            findings.append(_finding(root, provenance_path, "Protocol 2 provenance records are missing.")); continue
        index: dict[str, dict[str, Any]] = {}
        invalid = False
        for record in records:
            fields = _record_fields(record)
            if fields is None or fields[0] in index:
                invalid = True; break
            index[fields[0]] = record
        if invalid:
            findings.append(_finding(root, provenance_path, "Protocol 2 provenance contains a partial, duplicate, inconsistent, or incomplete immutable revision record.")); continue
        for iteration in bound:
            revision_id, subject_ref, reviewer_ref, status = iteration.get("revision"), iteration.get("subject_provenance"), iteration.get("reviewer_provenance"), iteration.get("status")
            if not (isinstance(revision_id, str) and revision_id and isinstance(subject_ref, str) and subject_ref):
                findings.append(_finding(root, manifest_path, "A bound Review Iteration requires revision and subject_provenance.")); continue
            subject = index.get(subject_ref)
            if subject is None:
                findings.append(_finding(root, manifest_path, "Subject provenance was not found; invented IDs are not evidence.")); continue
            sf = _record_fields(subject); assert sf is not None
            _, srole, sexec, sctx, srevision, simmutable = sf
            if srole not in {"implementation", "resolution"} or subject["source"].get("assurance") not in {"recorded", "verified"}:
                findings.append(_finding(root, manifest_path, "Review subject must be recorded/verified implementation or resolution provenance.")); continue
            if srevision != revision_id:
                findings.append(_finding(root, manifest_path, "Review subject provenance does not bind to the logical revision under review."))
            if simmutable[0] == "git_commit":
                if not _git_commit_exists(root, simmutable[1]):
                    findings.append(_finding(root, manifest_path, "C-026 review subject immutable git commit does not exist in the local repository."))
                elif _subject_changed_after_freeze(root, manifest_path, simmutable[1]):
                    findings.append(_finding(root, manifest_path, "C-026 review subject changed after its immutable revision freeze; create new subject provenance."))
            if status != "passed":
                continue
            if not isinstance(reviewer_ref, str) or not reviewer_ref:
                findings.append(_finding(root, manifest_path, "A passed Protocol 2 Review Iteration requires reviewer_provenance.")); continue
            reviewer = index.get(reviewer_ref)
            if reviewer is None:
                findings.append(_finding(root, manifest_path, "Reviewer provenance was not found; invented IDs are not proof of independence.")); continue
            rf = _record_fields(reviewer); assert rf is not None
            _, rrole, rexec, rctx, rrevision, rimmutable = rf
            if rrole != "review" or reviewer["source"].get("assurance") not in {"recorded", "verified"}:
                findings.append(_finding(root, manifest_path, "Reviewer provenance must be recorded/verified review provenance.")); continue
            if rrevision != revision_id:
                findings.append(_finding(root, manifest_path, "Reviewer provenance does not bind to the logical revision under review."))
            if rimmutable != simmutable:
                findings.append(_finding(root, manifest_path, "C-026 concrete revision binding failed: subject and Reviewer provenance reference different immutable revisions."))
            if sexec == rexec:
                findings.append(_finding(root, manifest_path, "Strict Review is not independent: Reviewer and subject share the same Execution."))
            if sctx == rctx:
                findings.append(_finding(root, manifest_path, "Strict Review is context-contaminated: Reviewer and subject share the same Execution Context."))
        if review.get("status") == "passed" and not any(isinstance(i, dict) and i.get("status") == "passed" for i in iterations):
            findings.append(_finding(root, manifest_path, "review.status is passed but no Review Iteration is passed."))
    return findings

def validate_project(project_root: Path, protocol_root: Path) -> ValidationResult:
    forge_dir = project_root / ".forge"
    if not forge_dir.is_dir():
        return ValidationResult((ValidationFinding("E_FORGE_NOT_INITIALIZED", ".forge/", "Forge is not initialized. Run `forge init` from this Git repository.", forge_dir),))
    try:
        config = load_project_configuration(forge_dir / "forge.yml")
    except (UnsupportedProtocolVersionError, InvalidProjectConfigurationError) as error:
        return ValidationResult((ValidationFinding(error.code, ".forge/forge.yml", str(error), forge_dir / "forge.yml"),))
    protocol_id = config["forge"]["protocol"]
    findings: list[ValidationFinding] = []
    flow_dir = forge_dir / "flows"
    if flow_dir.is_dir():
        for flow_path in sorted(flow_dir.glob("*.yml")):
            try: resolve_effective_flow(protocol_root, project_root, flow_path.stem, protocol_id)
            except UnknownCanonicalFlowError as error: findings.append(ValidationFinding("E_FORGE_UNKNOWN_CANONICAL_FLOW", str(flow_path.relative_to(project_root)), str(error), flow_path))
            except InvalidProjectFlowConfigurationError as error: findings.append(ValidationFinding("E_FORGE_INVALID_PROJECT_FLOW", str(flow_path.relative_to(project_root)), str(error), flow_path))
    try: resolve_effective_contract(protocol_root, project_root, protocol_id)
    except CanonicalContractUnavailableError as error: findings.append(ValidationFinding("E_FORGE_CANONICAL_CONTRACT_UNAVAILABLE", f"protocol/{protocol_id}/contract/engineering.md", str(error), protocol_root))
    if protocol_id == 2: findings.extend(_validate_protocol2_review_provenance(project_root))
    return ValidationResult(tuple(findings))
