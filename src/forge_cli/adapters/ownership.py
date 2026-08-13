"""Pure ownership and collision classification for Harness Adapter artifacts."""

from __future__ import annotations

from dataclasses import dataclass

from forge_cli.adapters.plan import OperationIntent, OwnershipMode


@dataclass(frozen=True)
class OwnershipDecision:
    intent: OperationIntent
    safe_to_apply: bool
    content: str | None = None


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
