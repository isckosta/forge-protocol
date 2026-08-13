"""Forge workspace boundary."""

from collections.abc import Mapping
from pathlib import Path, PurePosixPath
import shutil
from uuid import uuid4


class WorkspaceAlreadyInitializedError(RuntimeError):
    """Raised when a Forge workspace already exists."""


class InvalidWorkspacePlanError(ValueError):
    """Raised when requested workspace files cannot form a valid tree."""


def initialize_workspace(project_root: Path, files: Mapping[str, str]) -> Path:
    """Publish a Forge workspace only after the complete file set is staged."""
    project_root = project_root.resolve()
    target = project_root / ".forge"

    if target.exists():
        raise WorkspaceAlreadyInitializedError(str(target))

    normalized = _validate_workspace_plan(files)
    staging = project_root / f".forge.tmp-{uuid4().hex}"

    try:
        staging.mkdir()

        for relative, content in normalized.items():
            destination = staging.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content)

        if target.exists():
            raise WorkspaceAlreadyInitializedError(str(target))

        staging.rename(target)
        return target
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def _validate_workspace_plan(files: Mapping[str, str]) -> dict[PurePosixPath, str]:
    normalized: dict[PurePosixPath, str] = {}

    for raw_path, content in files.items():
        path = PurePosixPath(raw_path)

        if path.is_absolute() or not path.parts or ".." in path.parts or "." in path.parts:
            raise InvalidWorkspacePlanError(raw_path)

        normalized[path] = content

    paths = set(normalized)
    for path in paths:
        for parent in path.parents:
            if parent == PurePosixPath("."):
                break
            if parent in paths:
                raise InvalidWorkspacePlanError(str(path))

    return normalized
