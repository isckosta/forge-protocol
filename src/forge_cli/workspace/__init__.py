"""Forge workspace boundary."""

from collections.abc import Mapping
import os
from pathlib import Path, PurePosixPath
import shutil
from uuid import uuid4


class WorkspaceAlreadyInitializedError(RuntimeError):
    """Raised when a Forge workspace already exists."""


class WorkspaceInitializationInProgressError(RuntimeError):
    """Raised when another Forge initialization owns the project lock."""


class InvalidWorkspacePlanError(ValueError):
    """Raised when requested workspace files cannot form a valid tree."""


def initialize_workspace(project_root: Path, files: Mapping[str, str]) -> Path:
    """Publish a Forge workspace only after the complete file set is staged."""
    project_root = project_root.resolve()
    target = project_root / ".forge"

    if target.exists():
        raise WorkspaceAlreadyInitializedError(str(target))

    normalized = _validate_workspace_plan(files)
    lock_path = project_root / ".forge.init.lock"
    lock_fd: int | None = None
    lock_acquired = False
    staging: Path | None = None

    try:
        try:
            lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            lock_acquired = True
        except FileExistsError as error:
            raise WorkspaceInitializationInProgressError(str(lock_path)) from error

        os.write(lock_fd, f"pid={os.getpid()}\n".encode())
        os.close(lock_fd)
        lock_fd = None

        if target.exists():
            raise WorkspaceAlreadyInitializedError(str(target))

        staging = project_root / f".forge.tmp-{uuid4().hex}"
        staging.mkdir()

        for relative, content in normalized.items():
            destination = staging.joinpath(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")

        if target.exists():
            raise WorkspaceAlreadyInitializedError(str(target))

        staging.rename(target)
        staging = None
        return target
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
        if staging is not None and staging.exists():
            shutil.rmtree(staging)
        if lock_acquired:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


def _validate_workspace_plan(files: Mapping[str, str]) -> dict[PurePosixPath, str]:
    normalized: dict[PurePosixPath, str] = {}

    for raw_path, content in files.items():
        if "\\" in raw_path or "\x00" in raw_path:
            raise InvalidWorkspacePlanError(raw_path)

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
