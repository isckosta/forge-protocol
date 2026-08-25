from __future__ import annotations

from pathlib import Path
import hashlib
import subprocess

import yaml

from forge_cli.protocol_resources import resolve_protocol_root
from forge_cli.protocol_resolution import resolve_effective_flow
from forge_cli.validation import validate_project

from .change_resolution import (
    MergeReadinessOperationalError,
    affected_changes,
    changed_paths,
    is_material,
    tree_file,
)
from .policy import MaterialityPolicyError, classify_path, load_materiality_policy
from .models import (
    MergeReadinessEvaluation,
    MergeReadinessRequest,
    ReadinessCheck,
    ReadinessDiagnostic,
)


def _manifest(root: Path, change_id: str, head_revision: str) -> tuple[Path, dict]:
    changes = root / ".forge" / "changes"
    matches = []
    for path in sorted(changes.glob(f"{change_id}-*/manifest.yml")):
        matches.append(path)
    if len(matches) != 1:
        raise MergeReadinessOperationalError(
            f"Expected exactly one manifest for {change_id}, found {len(matches)}"
        )
    path = matches[0]
    data = yaml.safe_load(tree_file(root, head_revision, path.relative_to(root).as_posix())) or {}
    if not isinstance(data, dict):
        raise MergeReadinessOperationalError(f"Malformed manifest: {path}")
    return path, data


def _first_committed_record(root: Path, relative_path: str, record_id: str) -> dict | None:
    commits = subprocess.run(
        ["git", "log", "--reverse", "--format=%H", "--", relative_path],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if commits.returncode:
        return None
    for commit in commits.stdout.splitlines():
        try:
            data = yaml.safe_load(tree_file(root, commit, relative_path)) or {}
        except (MergeReadinessOperationalError, yaml.YAMLError, TypeError):
            continue
        for record in data.get("records", []) if isinstance(data, dict) else []:
            if isinstance(record, dict) and record.get("id") == record_id:
                return record
    return None


def _check_change(root: Path, change_id: str, head_revision: str) -> tuple[list[ReadinessCheck], list[ReadinessDiagnostic]]:
    path, manifest = _manifest(root, change_id, head_revision)
    checks: list[ReadinessCheck] = []
    diagnostics: list[ReadinessDiagnostic] = []
    relative = path.relative_to(root).as_posix()
    state = manifest.get("state", {}) if isinstance(manifest.get("state"), dict) else {}

    checks.append(ReadinessCheck("MR-STRUCTURAL", "pass", change_id, "Manifest loaded"))
    flow = manifest.get("flow", {}).get("current") if isinstance(manifest.get("flow"), dict) else None
    if flow not in {"fast", "standard", "full"}:
        diagnostics.append(ReadinessDiagnostic("MR-002", "Change Flow is missing or invalid", change_id, relative))
    verification = manifest.get("verification", {}).get("status") if isinstance(manifest.get("verification"), dict) else None
    if verification != "passed":
        diagnostics.append(ReadinessDiagnostic("MR-003", "VERIFICATION NOT READY", change_id, relative, "passed", str(verification)))
    verification_relative = f"{path.parent.relative_to(root).as_posix()}/verification.md"
    if verification == "passed":
        try:
            verification_text = tree_file(root, head_revision, verification_relative)
        except (MergeReadinessOperationalError, yaml.YAMLError, TypeError):
            verification_text = ""
        if "**PASS**" not in verification_text and "\nPASS\n" not in verification_text:
            diagnostics.append(ReadinessDiagnostic("MR-006", "Verification status is contradicted by verification.md", change_id, verification_relative))
    review = manifest.get("review", {}) if isinstance(manifest.get("review"), dict) else {}
    if review.get("status") != "passed":
        diagnostics.append(ReadinessDiagnostic("MR-004", "STRICT REVIEW NOT READY", change_id, relative, "passed", str(review.get("status"))))
    if review.get("status") == "passed":
        iterations = review.get("iterations")
        if isinstance(iterations, list) and not any(
            isinstance(item, dict) and item.get("status") == "passed" for item in iterations
        ):
            diagnostics.append(ReadinessDiagnostic("MR-012", "Review claims passed but has no passed iteration", change_id, relative))
        elif isinstance(iterations, list):
            passed = [item for item in iterations if isinstance(item, dict) and item.get("status") == "passed"]
            final_iteration = passed[-1] if passed else None
            if iterations and (not isinstance(iterations[-1], dict) or iterations[-1].get("status") != "passed"):
                diagnostics.append(ReadinessDiagnostic("MR-020", "Review history ends with a non-passed iteration", change_id, relative))
            provenance_relative = f"{path.parent.relative_to(root).as_posix()}/provenance.yml"
            try:
                provenance = yaml.safe_load(tree_file(root, head_revision, provenance_relative)) or {}
            except (MergeReadinessOperationalError, yaml.YAMLError, TypeError):
                provenance = {}
            records = provenance.get("records", []) if isinstance(provenance, dict) else []
            record_index = {item.get("id"): item for item in records if isinstance(item, dict)}
            if len(record_index) != len(records):
                diagnostics.append(ReadinessDiagnostic("MR-018", "Provenance contains duplicate record identities", change_id, relative))
            subject_record = record_index.get(final_iteration.get("subject_provenance")) if final_iteration else None
            reviewer_record = record_index.get(final_iteration.get("reviewer_provenance")) if final_iteration else None
            if not isinstance(reviewer_record, dict) or reviewer_record.get("role") != "review":
                diagnostics.append(ReadinessDiagnostic("MR-018", "Passed Review lacks admissible reviewer provenance", change_id, relative))
            subject_revision = subject_record.get("revision", {}) if isinstance(subject_record, dict) else {}
            if isinstance(subject_record, dict):
                anchored = _first_committed_record(root, provenance_relative, subject_record.get("id", ""))
                if anchored is None or anchored != subject_record:
                    diagnostics.append(ReadinessDiagnostic("MR-021", "Review subject provenance was rewritten or lacks committed authority", change_id, relative))
            subject_commit = subject_revision.get("commit") or subject_revision.get("immutable_ref", {}).get("value")
            if not isinstance(subject_commit, str) or len(subject_commit) != 40:
                diagnostics.append(ReadinessDiagnostic("MR-015", "REVIEW SUBJECT STALE: immutable subject provenance is missing", change_id, relative))
            else:
                ancestor = subprocess.run(
                    ["git", "merge-base", "--is-ancestor", subject_commit, head_revision],
                    cwd=root,
                    capture_output=True,
                    check=False,
                )
                if ancestor.returncode != 0:
                    diagnostics.append(ReadinessDiagnostic("MR-015", "REVIEW SUBJECT STALE", change_id, relative, head_revision, subject_commit))
                else:
                    change_root = path.parent.relative_to(root).as_posix()
                    delta = subprocess.run(
                        ["git", "diff", "--name-only", subject_commit, head_revision, "--", change_root],
                        cwd=root,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    allowed = {
                        f"{change_root}/manifest.yml",
                        f"{change_root}/provenance.yml",
                        f"{change_root}/review.md",
                    }
                    uncovered_paths = [item for item in delta.stdout.splitlines() if item and item not in allowed]
                    if delta.returncode != 0:
                        diagnostics.append(ReadinessDiagnostic("MR-015", "REVIEW SUBJECT STALE", change_id, relative, head_revision, subject_commit))
                    elif uncovered_paths:
                        # Protocol 2 Sec 5: the only paths that may differ
                        # WITHOUT renewing subject provenance are the three
                        # above. Any other change_root delta requires an
                        # explicit, anchored provenance record -- whose
                        # commit is an ancestor of (or equal to)
                        # head_revision -- declaring a scope that covers the
                        # specific path. Not an implicit tolerance keyed on
                        # manifest.state (Sec 5's own "MUST NOT be inferred
                        # from... membership in the Change directory
                        # generally"; Sec 14's "a manifest claim... is not
                        # sufficient authorization").
                        renewed_scope: set[str] = set()
                        for item in records:
                            if not (isinstance(item, dict) and item.get("role") in {"implementation", "resolution"}):
                                continue
                            renewal_commit = (
                                item.get("revision", {}).get("commit")
                                or item.get("revision", {}).get("immutable_ref", {}).get("value")
                            )
                            if not isinstance(renewal_commit, str) or len(renewal_commit) != 40:
                                continue
                            renewal_ancestor = subprocess.run(
                                ["git", "merge-base", "--is-ancestor", renewal_commit, head_revision],
                                cwd=root, capture_output=True, check=False,
                            )
                            if renewal_ancestor.returncode != 0:
                                continue
                            scope = item.get("scope")
                            if not (isinstance(scope, list) and scope):
                                continue
                            anchored_renewal = _first_committed_record(root, provenance_relative, item.get("id", ""))
                            if anchored_renewal is not None and anchored_renewal == item:
                                renewed_scope.update(p for p in scope if isinstance(p, str))
                        if any(item not in renewed_scope for item in uncovered_paths):
                            diagnostics.append(ReadinessDiagnostic("MR-015", "REVIEW SUBJECT STALE", change_id, relative, head_revision, subject_commit))
            verification_records = [
                item for item in records
                if isinstance(item, dict)
                and item.get("role") == "implementation"
                and isinstance(item.get("source"), dict)
                and item["source"].get("reference") == "verification.md"
                and item["source"].get("assurance") in {"recorded", "verified"}
            ]
            bound_verification_records = [
                item for item in verification_records
                if (
                    item.get("revision", {}).get("commit")
                    or item.get("revision", {}).get("immutable_ref", {}).get("value")
                ) == subject_commit
            ]
            if len(bound_verification_records) != 1 or not isinstance(subject_commit, str):
                diagnostics.append(ReadinessDiagnostic("MR-006", "Verification evidence is not bound to the immutable implementation subject", change_id, verification_relative, subject_commit))
            if isinstance(subject_record, dict) and isinstance(reviewer_record, dict):
                if subject_record.get("role") not in {"implementation", "resolution"}:
                    diagnostics.append(ReadinessDiagnostic("MR-018", "Review subject provenance has an invalid role", change_id, relative))
                subject_logical = subject_revision.get("id")
                reviewer_revision = reviewer_record.get("revision", {})
                reviewer_commit = reviewer_revision.get("commit") or reviewer_revision.get("immutable_ref", {}).get("value")
                if reviewer_commit != subject_commit:
                    diagnostics.append(ReadinessDiagnostic("MR-018", "Reviewer provenance does not bind to the reviewed subject", change_id, relative))
                if reviewer_revision.get("id") != subject_logical:
                    diagnostics.append(ReadinessDiagnostic("MR-018", "Reviewer provenance logical revision does not match the reviewed subject", change_id, relative))
                reviewer_source = reviewer_record.get("source", {})
                if reviewer_source.get("assurance") not in {"recorded", "verified"} or reviewer_source.get("observed_by") not in {"self", "operator", "adapter", "harness"}:
                    diagnostics.append(ReadinessDiagnostic("MR-018", "Reviewer provenance assurance/source is malformed", change_id, relative))
                subject_execution = subject_record.get("execution", {})
                reviewer_execution = reviewer_record.get("execution", {})
                if (
                    subject_execution.get("id") == reviewer_execution.get("id")
                    or subject_execution.get("context_id") == reviewer_execution.get("context_id")
                ):
                    diagnostics.append(ReadinessDiagnostic("MR-018", "Reviewer Execution and Context are not independent", change_id, relative))
    review_relative = f"{path.parent.relative_to(root).as_posix()}/review.md"
    if review.get("status") == "passed":
        try:
            review_text = tree_file(root, head_revision, review_relative)
        except (MergeReadinessOperationalError, yaml.YAMLError, TypeError):
            review_text = ""
        if "**PASS**" not in review_text and "\nPASS\n" not in review_text:
            diagnostics.append(ReadinessDiagnostic("MR-007", "Review status is contradicted by review.md", change_id, review_relative))
    if state.get("current") != "complete":
        diagnostics.append(ReadinessDiagnostic("MR-005", "COMPLETION NOT READY", change_id, relative, "complete", str(state.get("current"))))
    if state.get("current") == "complete":
        for required_name in ("verification.md", "review.md", "provenance.yml"):
            required_relative = f"{path.parent.relative_to(root).as_posix()}/{required_name}"
            try:
                tree_file(root, head_revision, required_relative)
            except MergeReadinessOperationalError:
                diagnostics.append(ReadinessDiagnostic("MR-016", "Completion claim lacks required repository-native evidence", change_id, required_relative))
    tdd = manifest.get("tdd") if isinstance(manifest.get("tdd"), dict) else {}
    if state.get("current") == "complete" and tdd.get("status") not in {"compliant", "not_applicable", "exception"}:
        diagnostics.append(ReadinessDiagnostic("MR-013", "Completion claims are inconsistent with TDD evidence", change_id, relative))
    decisions = manifest.get("decisions") if isinstance(manifest.get("decisions"), list) else []
    for decision in decisions:
        if isinstance(decision, dict) and decision.get("materiality") == "material" and decision.get("status") in {"open", "analyzing", "awaiting_decision"}:
            diagnostics.append(ReadinessDiagnostic("MR-014", "Material Decision remains unresolved", change_id, relative))
    artifacts = manifest.get("artifacts") if isinstance(manifest.get("artifacts"), dict) else {}
    project_config_path = root / ".forge" / "forge.yml"
    if not project_config_path.is_file():
        diagnostics.append(ReadinessDiagnostic("MR-901", "Project Flow configuration is missing", change_id, ".forge/forge.yml"))
    else:
        try:
            project_config = yaml.safe_load(tree_file(root, head_revision, ".forge/forge.yml")) or {}
            protocol_id = int(project_config.get("forge", {}).get("protocol", 1))
            flow_id = flow or project_config.get("flows", {}).get("default")
            effective = resolve_effective_flow(resolve_protocol_root(), root, flow_id, protocol_id)
            stages = effective["canonical"].get("stages", [])
            aliases = {"tdd_implementation": "tdd_evidence", "strict_review": "review", "documentation_impact": "documentation"}
            for stage in stages:
                if not isinstance(stage, dict) or stage.get("required") is not True:
                    continue
                stage_id = stage.get("id")
                if stage_id == "completion":
                    # Completion is a terminal lifecycle marker tracked via
                    # manifest.state.current (checked separately via MR-016),
                    # not a per-file Artifact with its own status entry.
                    continue
                key = aliases.get(stage_id, stage_id)
                if key in {"intent", "inspection", "discovery", "specification", "architecture", "test_design", "test_strategy", "plan", "tasks", "knowledge_capture"} and key not in artifacts:
                    diagnostics.append(ReadinessDiagnostic("MR-009", f"Required artifact is missing: {key}", change_id, relative))
                elif key in artifacts and artifacts.get(key) not in {"complete", "approved", "passed"}:
                    diagnostics.append(ReadinessDiagnostic("MR-009", f"Required artifact is not complete: {key}", change_id, relative, "complete", str(artifacts.get(key))))
            requirements = set(effective["canonical"].get("gates", {}).get("before_completion", {}).get("require", []))
            if "blocking_review_threads_resolved" in requirements and not (
                review.get("status") == "passed"
                and review.get("blockers", 0) == 0
                and review.get("majors", 0) == 0
            ):
                diagnostics.append(ReadinessDiagnostic("MR-009", "Blocking Review threads are not resolved according to the canonical Review evidence", change_id, relative))
            if "required_knowledge_capture_complete" in requirements and artifacts.get("knowledge_capture") not in {"complete", "approved", "passed"}:
                diagnostics.append(ReadinessDiagnostic("MR-009", "Required Knowledge Capture is not complete", change_id, relative))
            doc_state = manifest.get("documentation") if isinstance(manifest.get("documentation"), dict) else {}
            if "required_documentation_updated" in requirements and doc_state.get("update_required") is True and artifacts.get("documentation") not in {"complete", "approved", "passed"}:
                diagnostics.append(ReadinessDiagnostic("MR-009", "Required documentation update is not complete", change_id, relative))
            if "tdd_compliant_or_explicitly_excepted" in requirements and tdd.get("status") not in {"compliant", "exception", "not_applicable"}:
                diagnostics.append(ReadinessDiagnostic("MR-013", "TDD completion gate is not satisfied", change_id, relative))
        except Exception as error:
            diagnostics.append(ReadinessDiagnostic("MR-901", f"Cannot resolve effective Flow: {error}", change_id, relative))
    documentation = manifest.get("documentation") if isinstance(manifest.get("documentation"), dict) else {}
    if documentation.get("impact_evaluated") is not True:
        diagnostics.append(ReadinessDiagnostic("MR-009", "Documentation impact has not been evaluated", change_id, relative))
    if documentation.get("update_required") is True and artifacts.get("documentation") not in {"complete", "approved", "passed"}:
        diagnostics.append(ReadinessDiagnostic("MR-009", "Required documentation update is not complete", change_id, relative))
    if review.get("blockers", 0) > 0:
        diagnostics.append(ReadinessDiagnostic("MR-010", "Unresolved BLOCKER findings remain", change_id, relative))
    if review.get("majors", 0) > 0:
        diagnostics.append(ReadinessDiagnostic("MR-011", "Unresolved MAJOR findings remain", change_id, relative))
    if artifacts.get("plan") == "approved" and change_id >= "CHG-0025":
        provenance_relative = f"{path.parent.relative_to(root).as_posix()}/provenance.yml"
        digest = None
        try:
            provenance = yaml.safe_load(tree_file(root, head_revision, provenance_relative)) or {}
        except (MergeReadinessOperationalError, yaml.YAMLError, TypeError):
            provenance = {}
        approval_records = []
        for record in provenance.get("records", []) if isinstance(provenance, dict) else []:
            source = record.get("source") if isinstance(record, dict) else None
            if (
                isinstance(record, dict)
                and record.get("role") == "implementation"
                and isinstance(source, dict)
                and source.get("reference") == "plan.md#approval-record"
                and source.get("assurance") in {"recorded", "verified"}
                and source.get("observed_by") == "operator"
            ):
                approval_records.append(record)
        if len(approval_records) == 1:
            content_digest = approval_records[0].get("source", {}).get("content_digest", {})
            if isinstance(content_digest, dict) and content_digest.get("algorithm") == "sha256" and content_digest.get("path") == "plan.md":
                digest = content_digest.get("value")
        elif len(approval_records) > 1:
            diagnostics.append(ReadinessDiagnostic("MR-019", "Plan authorization is ambiguous", change_id, relative))
        plan_relative = f"{path.parent.relative_to(root).as_posix()}/plan.md"
        try:
            plan_text = tree_file(root, head_revision, plan_relative)
        except MergeReadinessOperationalError:
            plan_text = None
        if not isinstance(digest, str) or plan_text is None:
            diagnostics.append(ReadinessDiagnostic("MR-008", "PLAN AUTHORIZATION STALE", change_id, relative))
        else:
            canonical = plan_text.replace("\r\n", "\n")
            canonical = "\n".join(
                line for line in canonical.split("\n")
                if "<!-- forge:plan-approval-confirmation -->" not in line
                and "<!-- forge:plan-approval-record -->" not in line
            )
            expected_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if digest != expected_digest:
                diagnostics.append(ReadinessDiagnostic("MR-008", "PLAN AUTHORIZATION STALE", change_id, relative, expected_digest, digest))
    if not diagnostics:
        checks.append(ReadinessCheck("MR-COMPLETE", "pass", change_id, "Lifecycle claims are complete"))
    return checks, diagnostics


def evaluate_merge_readiness(root: Path, request: MergeReadinessRequest) -> MergeReadinessEvaluation:
    try:
        workspace = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, capture_output=True, text=True, check=False)
        if workspace.returncode != 0:
            raise MergeReadinessOperationalError("Cannot determine working tree state")
        if workspace.stdout.strip():
            raise MergeReadinessOperationalError("Working tree is dirty; merge readiness requires an unambiguous repository subject")
        current_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False)
        if current_head.returncode != 0 or current_head.stdout.strip() != request.head_revision:
            raise MergeReadinessOperationalError("Checked-out HEAD does not equal the requested merge subject")
        paths = changed_paths(root, request.base_revision, request.head_revision)
        try:
            policy = load_materiality_policy()
        except MaterialityPolicyError as error:
            raise MergeReadinessOperationalError(str(error)) from error
        material = tuple(path for path in paths if classify_path(path, policy) == "material")
        changes = affected_changes(root, paths, request.head_revision)
        checks: list[ReadinessCheck] = []
        diagnostics: list[ReadinessDiagnostic] = []
        if (root / ".forge" / "forge.yml").is_file():
            validation = validate_project(root, resolve_protocol_root())
            if not validation.passed:
                diagnostics.extend(
                    ReadinessDiagnostic(
                        "MR-002",
                        f"Structural validation failed: {finding.message}",
                        artifact=finding.artifact,
                    )
                    for finding in validation.findings
                )
        if material and not changes:
            diagnostics.append(ReadinessDiagnostic(
                "MR-001",
                "CHANGE PROVENANCE MISSING: material repository changes have no governing Forge Change",
            ))
        for path in paths:
            if classify_path(path, policy) == "ambiguous":
                diagnostics.append(ReadinessDiagnostic("MR-017", f"Ambiguous materiality classification: {path}"))
        for change_id in changes:
            c, d = _check_change(root, change_id, request.head_revision)
            checks.extend(c)
            diagnostics.extend(d)
        verdict = "ready" if not diagnostics else "blocked"
        return MergeReadinessEvaluation(request, changes, tuple(checks), tuple(diagnostics), verdict)
    except (MergeReadinessOperationalError, MaterialityPolicyError, yaml.YAMLError, TypeError) as error:
        diagnostic = ReadinessDiagnostic("MR-900", f"Operational/configuration failure: {error}")
        return MergeReadinessEvaluation(request, (), (), (diagnostic,), "operational")
