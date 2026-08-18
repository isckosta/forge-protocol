"""Read-only repository snapshots for Adapter planning."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Iterable, Mapping

from forge_cli.adapters.plan import digest_content
from forge_cli.adapters.planner import RepositoryArtifactState
from forge_cli.adapters.state import AdapterInstallationRecord, load_installation_record


class AdapterRepositoryError(RuntimeError):
    """Raised when a repository snapshot cannot be safely read."""


class InvalidAdapterRepositoryPathError(AdapterRepositoryError):
    """Raised for a generated path that is not confined to the project root."""


class InvalidAdapterRepositoryRecordError(AdapterRepositoryError):
    """Raised when the installation record cannot be read safely."""


@dataclass(frozen=True)
class AdapterRepositorySnapshot:
    """One immutable observation of all artifact state used for a plan."""

    artifacts: Mapping[str, RepositoryArtifactState]


def installation_record_path(project_root: Path, adapter_id: str) -> Path:
    _checked_path(f".forge/adapters/{adapter_id}/installation.yml")
    return Path(project_root).joinpath(".forge", "adapters", adapter_id, "installation.yml")


def load_optional_installation_record(
    project_root: Path,
    adapter_id: str,
) -> AdapterInstallationRecord | None:
    """Read the optional installation record exactly once."""
    root = _checked_project_root(project_root)
    record_path = installation_record_path(root, adapter_id)
    return _load_optional_record(root, record_path)


def snapshot_repository_artifacts(
    project_root: Path,
    artifact_paths: Iterable[str],
) -> AdapterRepositorySnapshot:
    """Read each requested artifact once, without creating or normalizing anything."""
    root = _checked_project_root(project_root)
    unique_paths = tuple(sorted(set(artifact_paths)))
    artifacts = {path: _snapshot_artifact(root, path) for path in unique_paths}
    return AdapterRepositorySnapshot(artifacts=MappingProxyType(artifacts))


def _checked_project_root(project_root: Path) -> Path:
    root = Path(project_root)
    if root.is_symlink() or not root.is_dir():
        raise AdapterRepositoryError("Adapter operations require a real project root directory.")
    return root


def _checked_path(relative_path: str) -> PurePosixPath:
    if not isinstance(relative_path, str) or not relative_path:
        raise InvalidAdapterRepositoryPathError("Adapter artifact path must be non-empty.")
    if "\\" in relative_path or "\x00" in relative_path:
        raise InvalidAdapterRepositoryPathError("Adapter artifact path is cross-platform ambiguous.")
    path = PurePosixPath(relative_path)
    if (
        path.is_absolute()
        or any(part in {"", ".", ".."} or ":" in part for part in path.parts)
        or path.as_posix() != relative_path
    ):
        raise InvalidAdapterRepositoryPathError(
            f"Adapter artifact path is not repository-relative: {relative_path!r}."
        )
    return path


def _safe_target(root: Path, relative_path: str) -> Path:
    path = _checked_path(relative_path)
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise InvalidAdapterRepositoryPathError(
                f"Adapter artifact path traverses a symlink: {relative_path!r}."
            )
    return root.joinpath(*path.parts)


def _load_optional_record(root: Path, record_path: Path) -> AdapterInstallationRecord | None:
    try:
        relative = record_path.relative_to(root).as_posix()
        safe_path = _safe_target(root, relative)
        if not safe_path.exists():
            return None
        if safe_path.is_symlink() or not safe_path.is_file():
            raise InvalidAdapterRepositoryRecordError("Adapter installation record is not a regular file.")
        return load_installation_record(safe_path)
    except AdapterRepositoryError:
        raise
    except Exception as error:
        raise InvalidAdapterRepositoryRecordError(
            f"Adapter installation record is invalid: {error}"
        ) from error


def _snapshot_artifact(root: Path, relative_path: str) -> RepositoryArtifactState:
    target = _safe_target(root, relative_path)
    if not target.exists():
        return RepositoryArtifactState(
            path=relative_path,
            exists=False,
            current_digest=None,
            expected_digest=None,
        )
    if target.is_symlink() or not target.is_file():
        raise InvalidAdapterRepositoryPathError(
            f"Adapter artifact is not a regular file: {relative_path!r}."
        )
    try:
        digest = digest_content(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        raise AdapterRepositoryError(
            f"Cannot safely read Adapter artifact: {relative_path!r}."
        ) from error
    return RepositoryArtifactState(
        path=relative_path,
        exists=True,
        current_digest=digest,
        expected_digest=None,
    )
