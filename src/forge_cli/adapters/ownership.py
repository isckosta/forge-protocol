"""Pure ownership and collision classification for Harness Adapter artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

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


def classify_artifact(
    *,
    ownership: OwnershipMode,
    exists: bool,
    current_digest: str | None,
    expected_digest: str | None,
    merge_result: str | None,
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
        if expected_digest is not None and current_digest == expected_digest:
            return OwnershipDecision(
                intent=OperationIntent.UPDATE,
                safe_to_apply=True,
            )

        return OwnershipDecision(
            intent=OperationIntent.CONFLICT,
            safe_to_apply=False,
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
