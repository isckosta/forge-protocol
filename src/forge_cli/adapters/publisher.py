"""Safe repository publication boundary for Harness Adapter plans."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
import tempfile
from uuid import uuid4

from forge_cli.adapters.plan import (
    AdapterOperation,
    AdapterPlan,
    OperationIntent,
    OwnershipMode,
    digest_content,
)
from forge_cli.adapters.state import (
    AdapterInstallationRecord,
    load_installation_record,
    write_installation_record,
)


class AdapterPublicationError(RuntimeError):
    """Base failure for Adapter publication."""


class AdapterPublicationConflictError(AdapterPublicationError):
    """Raised when repository state no longer satisfies a safe publication plan."""


class UnsafeAdapterPathError(AdapterPublicationError):
    """Raised when an Adapter path is unsafe or ambiguous across platforms."""


def _validate_adapter_id(adapter_id: str) -> None:
    if (
        not adapter_id
        or adapter_id in {".", ".."}
        or "/" in adapter_id
        or "\\" in adapter_id
        or ":" in adapter_id
        or "\x00" in adapter_id
    ):
        raise UnsafeAdapterPathError(f"Unsafe Adapter id: {adapter_id!r}")


def _safe_target(root: Path, relative_path: str) -> Path:
    if not relative_path or "\\" in relative_path or "\x00" in relative_path:
        raise UnsafeAdapterPathError(f"Unsafe Adapter artifact path: {relative_path!r}")

    pure = PurePosixPath(relative_path)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise UnsafeAdapterPathError(f"Unsafe Adapter artifact path: {relative_path!r}")
    if any(":" in part for part in pure.parts):
        raise UnsafeAdapterPathError(f"Cross-platform ambiguous Adapter path: {relative_path!r}")

    resolved_root = root.resolve()
    candidate = resolved_root.joinpath(*pure.parts)

    current = resolved_root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise UnsafeAdapterPathError(
                f"Adapter artifact path traverses a symlink: {relative_path!r}"
            )

    resolved_candidate = candidate.resolve(strict=False)
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise UnsafeAdapterPathError(
            f"Adapter artifact path escapes repository root: {relative_path!r}"
        ) from exc

    return candidate


def _replace_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.forge-tmp-{uuid4().hex}")
    try:
        temp_path.write_text(content, encoding="utf-8")
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _reserve_create_target(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.touch(exist_ok=False)
    except FileExistsError as exc:
        raise AdapterPublicationConflictError(
            f"Adapter create target appeared after planning: {path}."
        ) from exc


def _restore_bytes(path: Path, content: bytes | None) -> None:
    if content is None:
        if path.exists() or path.is_symlink():
            path.unlink()
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.forge-rollback-", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _current_digest(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AdapterPublicationConflictError(
            f"Cannot safely inspect current Adapter artifact: {path}"
        ) from exc
    return digest_content(content)


def _validate_record_matches_plan(
    plan: AdapterPlan,
    record: AdapterInstallationRecord,
) -> None:
    if record.adapter_id != plan.adapter_id:
        raise AdapterPublicationError(
            "Installation record Adapter id does not match the Adapter plan."
        )

    planned_generated = {
        operation.path: operation.content_digest
        for operation in plan.operations
        if operation.ownership is OwnershipMode.FORGE_OWNED
        and operation.intent
        in {
            OperationIntent.CREATE,
            OperationIntent.UPDATE,
            OperationIntent.UNCHANGED,
        }
    }
    recorded_generated = {
        artifact.path: artifact.digest for artifact in record.generated_artifacts
    }

    if planned_generated != recorded_generated:
        raise AdapterPublicationError(
            "Installation record generated artifact digests do not match the Adapter plan."
        )


def _preflight_operation(root: Path, operation: AdapterOperation) -> Path:
    target = _safe_target(root, operation.path)

    if operation.intent is OperationIntent.CONFLICT:
        raise AdapterPublicationConflictError(
            f"Adapter plan contains a conflicting operation for {operation.path}."
        )

    if operation.intent is OperationIntent.PRESERVE:
        return target

    if operation.intent is OperationIntent.UNCHANGED:
        if not target.exists() or target.is_symlink() or not target.is_file():
            raise AdapterPublicationConflictError(
                f"Adapter unchanged target is not a safe existing file: {operation.path}."
            )
        if operation.expected_current_digest is None:
            raise AdapterPublicationConflictError(
                f"Adapter unchanged target lacks an expected current digest: {operation.path}."
            )
        if _current_digest(target) != operation.expected_current_digest:
            raise AdapterPublicationConflictError(
                f"Adapter unchanged target changed after planning: {operation.path}."
            )
        return target

    if operation.intent is OperationIntent.DELETE_GENERATED:
        if not target.exists() or target.is_symlink() or not target.is_file():
            raise AdapterPublicationConflictError(
                f"Adapter delete target is not a safe existing file: {operation.path}."
            )
        if operation.expected_current_digest is None:
            raise AdapterPublicationConflictError(
                f"Adapter delete lacks an expected current digest: {operation.path}."
            )
        if _current_digest(target) != operation.expected_current_digest:
            raise AdapterPublicationConflictError(
                f"Adapter delete target changed after planning: {operation.path}."
            )
        return target

    if operation.content is None:
        raise AdapterPublicationError(
            f"Adapter operation {operation.path} has no publishable content."
        )

    if operation.intent is OperationIntent.CREATE:
        if target.exists() or target.is_symlink():
            raise AdapterPublicationConflictError(
                f"Adapter create target already exists: {operation.path}."
            )
        return target

    if operation.intent is OperationIntent.UPDATE:
        if not target.exists() or target.is_symlink() or not target.is_file():
            raise AdapterPublicationConflictError(
                f"Adapter update target is not a safe existing file: {operation.path}."
            )
        if operation.expected_current_digest is None:
            raise AdapterPublicationConflictError(
                f"Adapter update lacks an expected current digest: {operation.path}."
            )
        if _current_digest(target) != operation.expected_current_digest:
            raise AdapterPublicationConflictError(
                f"Adapter update target changed after planning: {operation.path}."
            )
        return target

    raise AdapterPublicationError(
        f"Unsupported Adapter operation intent: {operation.intent}."
    )


def _write_installation_record_atomically(
    path: Path,
    record: AdapterInstallationRecord,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.forge-tmp-{uuid4().hex}")
    try:
        write_installation_record(temporary, record)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def publish_adapter_plan(
    repository_root: Path,
    plan: AdapterPlan,
    installation_record: AdapterInstallationRecord,
) -> None:
    """Publish a precomputed Adapter plan without silently overwriting user state."""
    root = repository_root.resolve()
    _validate_adapter_id(plan.adapter_id)
    _validate_adapter_id(installation_record.adapter_id)

    if plan.conflicts:
        raise AdapterPublicationConflictError(
            "Adapter plan contains unresolved conflicts."
        )

    installation_relative = f".forge/adapters/{plan.adapter_id}/installation.yml"
    installation_path = _safe_target(root, installation_relative)

    targets: dict[str, Path] = {}
    for operation in plan.operations:
        targets[operation.path] = _preflight_operation(root, operation)

    _validate_record_matches_plan(plan, installation_record)

    applied: list[tuple[Path, bytes | None]] = []
    prior_installation = installation_path.read_bytes() if installation_path.exists() else None
    installation_existed = installation_path.exists()

    if installation_existed and all(
        operation.intent in {OperationIntent.PRESERVE, OperationIntent.UNCHANGED}
        for operation in plan.operations
    ) and load_installation_record(installation_path) == installation_record:
        return

    try:
        for operation in plan.operations:
            if operation.intent in {OperationIntent.PRESERVE, OperationIntent.UNCHANGED}:
                continue

            target = targets[operation.path]

            if operation.intent is OperationIntent.UPDATE:
                if (
                    operation.expected_current_digest is None
                    or not target.exists()
                    or target.is_symlink()
                    or _current_digest(target) != operation.expected_current_digest
                ):
                    raise AdapterPublicationConflictError(
                        f"Adapter update precondition changed before write: {operation.path}."
                    )
                original = target.read_bytes()
                applied.append((target, original))
                _replace_file(target, operation.content or "")
                continue

            if operation.intent is OperationIntent.CREATE:
                _reserve_create_target(target)
                applied.append((target, None))
                _replace_file(target, operation.content or "")
                continue

            if operation.intent is OperationIntent.DELETE_GENERATED:
                if (
                    operation.expected_current_digest is None
                    or not target.exists()
                    or target.is_symlink()
                    or not target.is_file()
                    or _current_digest(target) != operation.expected_current_digest
                ):
                    raise AdapterPublicationConflictError(
                        f"Adapter delete precondition changed before removal: {operation.path}."
                    )
                original = target.read_bytes()
                applied.append((target, original))
                target.unlink()
                continue

            raise AdapterPublicationError(
                f"Unsupported publishable Adapter operation intent: {operation.intent}."
            )

        _write_installation_record_atomically(installation_path, installation_record)
    except AdapterPublicationConflictError:
        for target, original in reversed(applied):
            _restore_bytes(target, original)
        if installation_existed:
            _restore_bytes(installation_path, prior_installation)
        elif installation_path.exists():
            installation_path.unlink()
        raise
    except Exception as exc:
        for target, original in reversed(applied):
            try:
                _restore_bytes(target, original)
            except OSError:
                pass
        try:
            if installation_existed:
                _restore_bytes(installation_path, prior_installation)
            elif installation_path.exists():
                installation_path.unlink()
        except OSError:
            pass
        if isinstance(exc, AdapterPublicationError):
            raise
        raise AdapterPublicationError("Adapter publication failed and was rolled back.") from exc
