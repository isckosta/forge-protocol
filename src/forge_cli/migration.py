"""Forge repository-native migration boundary.

Recognizes exactly one schema family: `forge/execution-provenance@1` ->
`@2`, the one case that is both a real, live-instance case and a
byte-identical superset for every non-`delegated_task` record
(protocol/compatibility.md's own CHG-0015 text). `forge/change@1` is
never migrated (compatibility.md forbids it); `forge/adapter-installation@1`
and `forge/policy/review@1` are out of scope for two different reasons
(see CHG-0019 discovery.md/architecture.md) and are never scanned here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

_SOURCE_SCHEMA = "forge/execution-provenance@1"
_TARGET_SCHEMA = "forge/execution-provenance@2"


@dataclass(frozen=True)
class MigrationCandidate:
    change_id: str
    path: Path


@dataclass(frozen=True)
class MigrationResult:
    change_id: str
    path: Path


def _is_safe_v1_provenance(path: Path) -> bool:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return False
    if not isinstance(data, dict) or data.get("schema") != _SOURCE_SCHEMA:
        return False
    records = data.get("records")
    if not isinstance(records, list):
        return False
    return not any(
        isinstance(record, dict) and record.get("role") == "delegated_task"
        for record in records
    )


def find_candidates(project_root: Path) -> tuple[MigrationCandidate, ...]:
    """Read-only scan for the one recognized, safe migration case."""
    changes_dir = Path(project_root) / ".forge" / "changes"
    if not changes_dir.is_dir():
        return ()

    candidates: list[MigrationCandidate] = []
    for change_dir in sorted(changes_dir.iterdir()):
        provenance_path = change_dir / "provenance.yml"
        if not provenance_path.is_file():
            continue
        if _is_safe_v1_provenance(provenance_path):
            candidates.append(
                MigrationCandidate(change_id=change_dir.name, path=provenance_path)
            )
    return tuple(candidates)


def apply_migrations(
    project_root: Path, candidates: tuple[MigrationCandidate, ...]
) -> tuple[MigrationResult, ...]:
    """Rewrite exactly the `schema:` line for each candidate.

    Exact string replacement, not YAML re-serialization: re-emitting via
    `yaml.safe_dump` could reorder keys or change quoting/formatting,
    which would violate "no other byte in the file changes" (Contract
    C-075, this Change's FR-003). Re-checks each candidate is still a
    safe v1 provenance file immediately before rewriting it, so a stale
    `candidates` tuple can never cause a double-migration or an
    out-of-date file to be silently overwritten.
    """
    results: list[MigrationResult] = []
    for candidate in candidates:
        if not _is_safe_v1_provenance(candidate.path):
            continue
        original = candidate.path.read_text(encoding="utf-8")
        rewritten = original.replace(_SOURCE_SCHEMA, _TARGET_SCHEMA, 1)
        candidate.path.write_text(rewritten, encoding="utf-8")
        results.append(MigrationResult(change_id=candidate.change_id, path=candidate.path))
    return tuple(results)
