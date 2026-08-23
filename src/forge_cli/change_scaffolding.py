"""Pure planning and rendering for repository-native Change scaffolds."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable
from typing import Any

import yaml


_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_CHANGE_DIR_RE = re.compile(r"^CHG-(?P<number>[0-9]{4,})-[a-z0-9]+(?:-[a-z0-9]+)*$")

_STAGE_FILES: dict[str, tuple[str, str]] = {
    "intent": ("intent.md", "intent"),
    "inspection": ("inspection.md", "inspection"),
    "discovery": ("discovery.md", "discovery"),
    "specification": ("specification.md", "specification"),
    "specification_review": ("specification-review.md", "specification_review"),
    "architecture": ("architecture.md", "architecture"),
    "test_design": ("test-design.md", "test_design"),
    "test_strategy": ("test-strategy.md", "test_strategy"),
    "plan": ("plan.md", "plan"),
    "tasks": ("tasks.md", "tasks"),
    "tdd_implementation": ("tdd-evidence.yml", "tdd_evidence"),
    "verification": ("verification.md", "verification"),
    "strict_review": ("review.md", "review"),
    "knowledge_capture": ("knowledge-capture.md", "knowledge_capture"),
}


@dataclass(frozen=True)
class ScaffoldPlan:
    """The complete, ordered file set prepared before publication."""

    files: dict[str, str]


class ChangeRollbackIncompleteError(OSError):
    """Publication failed and unknown content prevented complete rollback."""

    code = "E_FORGE_CHANGE_ROLLBACK_INCOMPLETE"


def validate_slug(slug: str) -> str:
    if not isinstance(slug, str) or _SLUG_RE.fullmatch(slug) is None:
        raise ValueError(f"Invalid Change slug: {slug!r}")
    return slug


def allocate_change_number(changes_root: Path) -> int:
    highest = 0
    if not changes_root.is_dir():
        return 1
    for entry in changes_root.iterdir():
        if not entry.is_dir():
            continue
        match = _CHANGE_DIR_RE.fullmatch(entry.name)
        if match is not None:
            highest = max(highest, int(match.group("number")))
    return highest + 1


def _title(slug: str) -> str:
    return " ".join(segment[:1].upper() + segment[1:] for segment in slug.split("-"))


def _frontmatter(artifact: str, change_id: str, status: str, title: str) -> str:
    heading = (
        f"# {change_id} · Specification"
        if artifact == "specification"
        else f"# {change_id} · Test Design"
        if artifact == "test_design"
        else f"# {change_id} · {title}"
        if artifact == "intent"
        else f"# {artifact.replace('_', ' ').title()} — {change_id} {title}"
    )
    return (
        "---\n"
        "forge:\n"
        f"  artifact: {artifact}\n"
        "  schema: 1\n"
        f"change: {change_id}\n"
        f"status: {status}\n"
        "---\n\n"
        f"{heading}\n\n"
    )


def _markdown(artifact: str, change_id: str, title: str, flow_id: str | None = None) -> str:
    content = _frontmatter(artifact, change_id, "active" if artifact == "intent" else "pending", title)
    if artifact == "intent":
        if flow_id is None:
            raise ValueError("Intent scaffolds require the selected Flow.")
        return content + (
            "> **Change Intent**\n"
            ">\n"
            "> State the intended change in one or two sentences. Keep this as an executive summary, not a full Goal.\n"
            "\n"
            "## Overview\n"
            "| | |\n"
            "|---|---|\n"
            f"| **Change** | {change_id} |\n"
            f"| **Flow** | {flow_id.upper()} |\n"
            "| **Status** | Active |\n"
            "\n"
            "## Problem\n\n"
            "Describe the problematic domain or user behavior, who or what it affects, and why the current behavior is insufficient.\n"
            "\n"
            "## Goal\n\n"
            "State the concrete objective of the Change without prescribing implementation. Add a short numbered list when multiple properties must hold.\n"
            "\n"
            "## Scope\n\n"
            "Describe the business, operational, or conceptual areas this Change covers. Do not list files or functions.\n"
            "\n"
            "## Out of Scope\n\n"
            "State what this Change explicitly does not cover. Use this boundary to prevent opportunistic expansion.\n"
            "\n"
            "## Success Criteria\n\n"
            "Describe the high-level reality that must exist when the Change is complete. Do not turn this into a test plan.\n"
        )
    sections = {
        "inspection": "## Inspection\n\nRecord the relevant inspection findings.\n",
        "discovery": "## Executive Summary\n\nRecord the strongest discovery and implication.\n\n## Investigation\n\nRecord evidence.\n",
        "specification": (
            "> **Change Contract**\n"
            ">\n"
            "> This Specification defines the behaviors, constraints, and verifiable conditions that the Change must satisfy.\n"
            "\n"
            "## Overview\n\n"
            "| | |\n"
            "|---|---|\n"
            f"| **Change** | {change_id} |\n"
            f"| **Flow** | {flow_id.upper()} |\n"
            "| **Status** | Draft |\n"
            "\n"
            "## Summary\n\n"
            "State the expected outcome and the contract boundary in a few sentences.\n"
            "\n"
            "## Classification\n\n"
            "Record the selected Flow and the semantic reason for it.\n"
            "\n"
            "## User Stories\n\n"
            "User Stories are optional behavioral context. Include this section only when a meaningful actor, concrete capability, and outcome add information; otherwise remove it. Do not invent a persona to satisfy the template.\n"
            "\n"
            "## Functional Requirements\n\n"
            "Each requirement is an independent, verifiable contract. A Requirement without a User Story is valid.\n"
            "\n"
            "### FR-001 · <requirement title>\n"
            "Stories: <US identifiers, when applicable>\n"
            "Origin: <finding reference, when applicable>\n"
            "Priority: <priority, when used>\n"
            "\n"
            "#### Requirement\n"
            "Write the normative behavior.\n"
            "\n"
            "#### Expected Behavior\n"
            "Describe important rules and consequences only when they add information.\n"
            "\n"
            "#### Boundary\n"
            "State an explicit limit only when the requirement needs one.\n"
            "\n"
            "#### Acceptance\n"
            "AC-001\n"
            "Given <initial condition>\n"
            "When <action>\n"
            "Then <observable result>\n"
            "\n"
            "## Non-functional Requirements\n\n"
            "Add NFR-xxx entries only when applicable. They do not require a User Story.\n"
            "\n"
            "## Constraints\n\n"
            "Add CON-xxx entries only when they restrict the solution or Change.\n"
            "\n"
            "## Traceability Matrix\n\n"
            "Use this as an index across Discovery, User Stories, Requirements, and Acceptance; the relationships on the entities remain authoritative. Omit User Story columns when no Stories apply.\n"
            "\n"
            "## Compatibility Statement\n\n"
            "Describe compatibility with existing behavior, artifacts, Protocol versions, or explicitly state why it is not materially affected.\n"
            "\n"
            "## Specification Gate\n\n"
            "Record the evidence that this Specification is complete, internally consistent, and ready for the next Flow stage.\n"
            "\n"
            "## Out of Scope\n\n"
            "List exclusions and boundaries.\n"
        ),
        "specification_review": "## Verdict\n\n**PENDING**\n\n## Findings\n\nRecord findings.\n\n## Checked and found sound\n\nRecord sound claims.\n\n## Conclusion\n\nRecord the conclusion.\n",
        "architecture": "## Solution Summary\n\nDescribe the selected solution.\n\n## Architectural Goals\n\nList goals.\n",
        "test_design": (
            "> Verification Design\n"
            "\n"
            "## Overview\n\n"
            "| | |\n"
            "|---|---|\n"
            f"| **Change** | {change_id} |\n"
            f"| **Flow** | {flow_id.upper()} |\n"
            "| **Status** | Draft |\n"
            "\n"
            "## Test Strategy\n\n"
            "Describe how this Change will be demonstrated before Implementation. Group scenarios into Layers only when that adds clarity (e.g. Domain, API, Persistence, CLI, Harness, Manual Acceptance); a single Layer is valid for a small Change.\n"
            "\n"
            "| Layer | Scope | Method |\n"
            "|---|---|---|\n"
            "| Layer A | <scope> | Automated |\n"
            "\n"
            "## Coverage Map\n\n"
            "List every Requirement this Change must verify before Implementation, with the Scenario that covers it. Include a Story column only when User Stories apply; a Requirement without a User Story is valid.\n"
            "\n"
            "| Requirement | Scenario | Method |\n"
            "|---|---|---|\n"
            "| FR-001 | TD-001 | Automated |\n"
            "\n"
            "## Layer A · <name>\n"
            "\n"
            "### TD-001 · <Scenario title>\n"
            "Requirements: FR-001\n"
            "Stories: <US identifiers, when applicable>\n"
            "Type: <Unit | Integration | Domain Integration | Manual Acceptance>\n"
            "Priority: <priority, when used>\n"
            "\n"
            "#### Purpose\n"
            "State the property this scenario proves, not the test's name. A weak Purpose restates the mechanism; a strong one explains the consequence a wrong Implementation would cause.\n"
            "\n"
            "#### Preconditions\n"
            "State only the initial state this scenario actually depends on. Omit this section when there is none.\n"
            "\n"
            "#### Scenario\n"
            "Given <initial condition>\n"
            "When <action>\n"
            "Then <observable result>\n"
            "\n"
            "#### Evidence\n"
            "State what observable material will exist to support the result: exit code, persisted row, emitted event, HTTP status, log, snapshot, test result, or manual observation.\n"
            "\n"
            "#### Failure Condition\n"
            "State what invalidates this scenario as evidence, including a false positive, not only what a failing assertion looks like.\n"
            "\n"
            "#### Boundary\n"
            "State what this scenario does not prove, only when it could reasonably be mistaken for proving more. Omit when there is no such risk.\n"
            "\n"
            "## Manual Acceptance\n\n"
            "Use `Type: Manual Acceptance` for a property that depends on human or real-Harness interaction and cannot reasonably be checked by tooling. A Manual Acceptance scenario still needs Preconditions, explicit operator instructions, observable Evidence, and a Failure Condition; it MUST NOT be presented as an automated guarantee.\n"
            "\n"
            "## Valid RED\n\n"
            "When TDD applies, RED is valid only when the test fails for the expected behavioral reason. A RED caused by a syntax error, a broken import, an invalid fixture, missing configuration, or unrelated infrastructure unavailability is not valid evidence and must be fixed and re-run before it counts.\n"
            "\n"
            "## Requirement Coverage\n\n"
            "| Requirement | Automated | Manual | Status |\n"
            "|---|---|---|---|\n"
            "| FR-001 | TD-001 | — | Covered |\n"
            "\n"
            "## Coverage Gaps\n\n"
            "State explicitly that no mandatory Requirement remains without a verification strategy, or list each gap. A critical Requirement that cannot be verified is a Specification problem, not an Implementation problem.\n"
            "\n"
            "## Test Design Gate\n\n"
            "Record that every mandatory Requirement has a verification strategy, critical scenarios have a clear Purpose, Failure Conditions are defined, automated and Manual Acceptance are separated, valid RED is defined when TDD applies, and no Requirement remains without known coverage.\n"
        ),
        "test_strategy": "## Objective\n\nState the test strategy objective.\n\n## Strategy\n\n## TDD-001 — <behavior>\n\nDefine the test case.\n\n## Completion Criteria\n\nList completion criteria.\n",
        "plan": "1. Describe the first approved work item and files.\n\n## Implementation Boundary\n\nReaching `plan_complete` is not authorization to begin Implementation.\n",
        "tasks": "- [ ] T-001 <work item>\n\n## Status\n\nNo task has started.\n",
        "verification": "## Result\n\n**PENDING**\n\n## Summary\n\nRecord verification results.\n\n## Test Evidence\n\n## Forge Evidence\n\n## Conclusion\n\n",
        "review": "## Verdict\n\n**PENDING**\n\n## Iteration 1 — PENDING\n\nRecord Strict Review findings.\n",
        "knowledge_capture": "## What Changed\n\nRecord the durable change.\n\n## Durable Knowledge\n\n## Consequences for Future Changes\n\n## References\n\n",
    }
    return content + sections[artifact]


def _manifest(
    *,
    change_id: str,
    title: str,
    flow_id: str,
    artifact_statuses: Mapping[str, str],
    behavioral: bool,
) -> str:
    manifest: dict[str, Any] = {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": change_id, "title": title, "kind": "feature"},
        "flow": {"initial": flow_id, "current": flow_id, "escalations": []},
        "state": {"current": "intent"},
        "artifacts": dict(artifact_statuses),
        "requirements": {"total": 0, "implemented": 0, "verified": 0},
        "tdd": (
            {"status": "pending"}
            if behavioral
            else {"status": "not_applicable", "reason": "The scaffold was created as non-behavioral."}
        ),
        "verification": {"status": "pending"},
        "review": {
            "status": "pending",
            "iteration": 0,
            "blockers": 0,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "iterations": [],
        },
        "documentation": {"impact_evaluated": False},
    }
    return yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True)


def render_scaffold(
    *,
    change_id: str,
    slug: str,
    flow_id: str,
    flow_data: Mapping[str, Any],
    behavioral: bool = True,
) -> ScaffoldPlan:
    validate_slug(slug)
    title = _title(slug)
    stages = flow_data.get("stages")
    if not isinstance(stages, list):
        raise ValueError("Canonical Flow has no valid stages list.")

    files: dict[str, str] = {}
    statuses: dict[str, str] = {}
    for stage in stages:
        if not isinstance(stage, Mapping):
            continue
        stage_id = stage.get("id")
        if stage_id in {"test_design", "tdd_implementation"} and not behavioral:
            continue
        mapping = _STAGE_FILES.get(stage_id)
        if mapping is None:
            continue
        path, artifact = mapping
        if path.endswith(".yml"):
            if artifact == "tdd_evidence":
                files[path] = yaml.safe_dump(
                    {"schema": "forge/tdd-evidence@1", "change": change_id, "status": "active", "cycle_count": 0, "cycles": []},
                    sort_keys=False,
                )
            else:
                raise ValueError(f"Unsupported YAML scaffold artifact: {stage_id}")
        else:
            files[path] = _markdown(artifact, change_id, title, flow_id)
        statuses[artifact] = "active" if artifact == "intent" else (
            "active" if artifact == "tdd_evidence" else "pending"
        )

    if flow_id == "fast":
        statuses["documentation_impact"] = "pending"
    else:
        statuses["documentation"] = "pending"
    files["manifest.yml"] = _manifest(
        change_id=change_id,
        title=title,
        flow_id=flow_id,
        artifact_statuses=statuses,
        behavioral=behavioral,
    )
    return ScaffoldPlan(files=files)


def publish_scaffold(
    target: Path,
    plan: ScaffoldPlan,
    *,
    before_claim: Callable[[], None] | None = None,
    write_file: Callable[[Path, str], None] | None = None,
) -> None:
    """Publish a prepared scaffold without overwriting an existing target."""
    target = Path(target)
    if target.exists():
        raise FileExistsError(target)
    if before_claim is not None:
        before_claim()
    created_directories: list[Path] = []
    parent = target.parent
    missing_parents: list[Path] = []
    while not parent.exists():
        missing_parents.append(parent)
        parent = parent.parent
    for directory in reversed(missing_parents):
        directory.mkdir()
        created_directories.append(directory)
    target.mkdir()
    created_directories.append(target)
    writer = write_file or _exclusive_write
    created: list[Path] = []
    try:
        for relative_path, content in plan.files.items():
            destination = target / relative_path
            writer(destination, content)
            created.append(destination)
    except Exception as publication_error:
        rollback_errors: list[Exception] = []
        for path in reversed(created):
            try:
                path.unlink()
            except FileNotFoundError:
                pass
            except OSError as error:
                rollback_errors.append(error)
        try:
            remaining = tuple(target.iterdir())
        except OSError as error:
            rollback_errors.append(error)
            remaining = (target,)
        if remaining:
            raise ChangeRollbackIncompleteError(str(target)) from publication_error
        try:
            target.rmdir()
            created_directories.remove(target)
            for directory in reversed(created_directories):
                directory.rmdir()
        except OSError as error:
            rollback_errors.append(error)
        if rollback_errors:
            raise ChangeRollbackIncompleteError(str(target)) from publication_error
        raise


def _exclusive_write(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8") as handle:
        handle.write(content)
