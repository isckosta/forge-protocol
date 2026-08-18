"""Pure ownership and collision classification for Harness Adapter artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Iterable, Mapping

from forge_cli.adapters.plan import OperationIntent, OwnershipMode
from forge_cli.adapters.state import AdapterInstallationRecord


@dataclass(frozen=True)
class OwnershipDecision:
    intent: OperationIntent
    safe_to_apply: bool
    content: str | None = None


class DriftKind(StrEnum):
    MODIFIED = "modified"
    MISSING = "missing"


@dataclass(frozen=True)
class GeneratedDrift:
    path: str
    kind: DriftKind
    expected_digest: str
    observed_digest: str | None


class InvalidAdapterPublicationOwnershipError(ValueError):
    """Raised when generated paths are not bound to a safe publication root."""


def _checked_publication_path(path: str, *, allow_repository_root: bool) -> PurePosixPath:
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        raise InvalidAdapterPublicationOwnershipError(
            f"Invalid Adapter publication path: {path!r}."
        )
    pure = PurePosixPath(path)
    if allow_repository_root and path == ".":
        return pure
    if (
        pure.is_absolute()
        or pure.as_posix() != path
        or any(part in {"", ".", ".."} or ":" in part for part in pure.parts)
    ):
        raise InvalidAdapterPublicationOwnershipError(
            f"Invalid Adapter publication path: {path!r}."
        )
    return pure


def _reject_canonical_forge_path(path: PurePosixPath) -> None:
    if path.parts and path.parts[0] == ".forge":
        raise InvalidAdapterPublicationOwnershipError(
            f"Canonical Forge state cannot be Adapter-generated: {path.as_posix()!r}."
        )


def require_publication_root_ownership(
    publication_root: str | None,
    artifact_paths: Iterable[str],
) -> None:
    """Require every artifact to be a strict descendant of a non-canonical root."""
    if publication_root is None:
        raise InvalidAdapterPublicationOwnershipError(
            "Adapter installation record has no publication-root ownership metadata."
        )
    root = _checked_publication_path(publication_root, allow_repository_root=True)
    _reject_canonical_forge_path(root)

    for artifact_path in artifact_paths:
        artifact = _checked_publication_path(
            artifact_path,
            allow_repository_root=False,
        )
        _reject_canonical_forge_path(artifact)
        if root not in artifact.parents:
            raise InvalidAdapterPublicationOwnershipError(
                f"Generated Adapter path {artifact_path!r} is not below recorded "
                f"publication root {publication_root!r}."
            )


def require_recorded_publication_ownership(
    record: AdapterInstallationRecord,
) -> None:
    require_publication_root_ownership(
        record.publication_root,
        (artifact.path for artifact in record.generated_artifacts),
    )


def classify_artifact(
    *,
    ownership: OwnershipMode,
    exists: bool,
    current_digest: str | None,
    expected_digest: str | None,
    merge_result: str | None,
    desired_digest: str | None = None,
) -> OwnershipDecision:
    """Classify an artifact without reading or mutating filesystem state."""

    if not exists:
        return OwnershipDecision(
            intent=OperationIntent.CREATE,
            safe_to_apply=True,
        )

    if ownership is OwnershipMode.USER_OWNED:
        return OwnershipDecision(
            intent=OperationIntent.PRESERVE,
            safe_to_apply=False,
        )

    if ownership is OwnershipMode.FORGE_OWNED:
        if expected_digest is None or current_digest != expected_digest:
            return OwnershipDecision(
                intent=OperationIntent.CONFLICT,
                safe_to_apply=False,
            )

        return OwnershipDecision(
            intent=(
                OperationIntent.UNCHANGED
                if desired_digest is not None and current_digest == desired_digest
                else OperationIntent.UPDATE
            ),
            safe_to_apply=True,
        )

    if ownership is OwnershipMode.SHARED:
        if merge_result is not None:
            return OwnershipDecision(
                intent=OperationIntent.UPDATE,
                safe_to_apply=True,
                content=merge_result,
            )

        return OwnershipDecision(
            intent=OperationIntent.CONFLICT,
            safe_to_apply=False,
        )

    raise ValueError(f"Unsupported ownership mode: {ownership!r}")


def detect_generated_drift(
    record: AdapterInstallationRecord,
    observed_digests: Mapping[str, str | None],
) -> tuple[GeneratedDrift, ...]:
    """Compare recorded generated state with already-observed content digests."""
    findings: list[GeneratedDrift] = []

    for artifact in record.generated_artifacts:
        observed = observed_digests.get(artifact.path)
        if observed == artifact.digest:
            continue

        findings.append(
            GeneratedDrift(
                path=artifact.path,
                kind=DriftKind.MISSING if observed is None else DriftKind.MODIFIED,
                expected_digest=artifact.digest,
                observed_digest=observed,
            )
        )

    return tuple(findings)


def classify_recorded_forge_owned(
    *,
    expected_digest: str,
    exists: bool,
    current_digest: str | None,
) -> OwnershipDecision:
    """Classify a recorded Forge-owned artifact using its expected generated digest."""
    return classify_artifact(
        ownership=OwnershipMode.FORGE_OWNED,
        exists=exists,
        current_digest=current_digest,
        expected_digest=expected_digest,
        merge_result=None,
    )
