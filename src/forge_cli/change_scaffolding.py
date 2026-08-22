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
    return (
        "---\n"
        "forge:\n"
        f"  artifact: {artifact}\n"
        "  schema: 1\n"
        f"change: {change_id}\n"
        f"status: {status}\n"
        "---\n\n"
        f"# {artifact.replace('_', ' ').title()} — {change_id} {title}\n\n"
    )


def _markdown(artifact: str, change_id: str, title: str) -> str:
    content = _frontmatter(artifact, change_id, "active" if artifact == "intent" else "pending", title)
    sections = {
        "intent": "## Summary\n\nDescribe the intended outcome.\n\n## Problem\n\nDescribe the problem.\n\n## Desired Outcome\n\nState the desired outcome.\n\n## Scope\n\nList the scope.\n\n## Out of Scope\n\nList exclusions.\n\n## Success Criteria\n\nList measurable criteria.\n",
        "inspection": "## Inspection\n\nRecord the relevant inspection findings.\n",
        "discovery": "## Executive Summary\n\nRecord the strongest discovery and implication.\n\n## Investigation\n\nRecord evidence.\n",
        "specification": "## Summary\n\nState the expected behavior.\n\n## Classification\n\nRecord the selected Flow and reason.\n\n## Functional Requirements\n\n## FR-001 — <requirement>\n\nDescribe a requirement.\n\n## Acceptance Criteria\n\n## AC-001 — <criterion>\n\nDescribe acceptance evidence.\n\n## Out of Scope\n\nList exclusions.\n",
        "specification_review": "## Verdict\n\n**PENDING**\n\n## Findings\n\nRecord findings.\n\n## Checked and found sound\n\nRecord sound claims.\n\n## Conclusion\n\nRecord the conclusion.\n",
        "architecture": "## Solution Summary\n\nDescribe the selected solution.\n\n## Architectural Goals\n\nList goals.\n",
        "test_design": "## Objective\n\nState the test objective.\n\n## Strategy\n\n## TDD-001 — <behavior>\n\nDefine RED, GREEN, and REFACTOR evidence.\n\n## Completion Criteria\n\nList completion criteria.\n",
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
            files[path] = _markdown(artifact, change_id, title)
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
            created.append(destination)
            writer(destination, content)
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
