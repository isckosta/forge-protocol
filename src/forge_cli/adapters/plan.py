"""Canonical immutable Harness Adapter planning models."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Iterable


def supports_executable_bit() -> bool:
    """Executable file modes are only meaningful on POSIX platforms.

    A single indirection so planning, publication, and diagnostics agree on
    what "this platform models an executable bit" means -- and so a test can
    exercise the non-POSIX path without patching ``os.name`` globally.
    """
    return os.name == "posix"


class OwnershipMode(StrEnum):
    FORGE_OWNED = "forge_owned"
    USER_OWNED = "user_owned"
    SHARED = "shared"


class OperationIntent(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    UNCHANGED = "unchanged"
    PRESERVE = "preserve"
    CONFLICT = "conflict"
    DELETE_GENERATED = "delete_generated"


def digest_content(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AdapterOperation:
    path: str
    ownership: OwnershipMode
    intent: OperationIntent
    content_digest: str
    content: str | None = None
    expected_current_digest: str | None = None
    executable: bool = False

    @classmethod
    def from_content(
        cls,
        *,
        path: str,
        ownership: OwnershipMode,
        intent: OperationIntent,
        content: str,
        expected_current_digest: str | None = None,
        executable: bool = False,
    ) -> "AdapterOperation":
        return cls(
            path=path,
            ownership=ownership,
            intent=intent,
            content_digest=digest_content(content),
            content=content,
            expected_current_digest=expected_current_digest,
            executable=executable,
        )


@dataclass(frozen=True, init=False)
class AdapterPlan:
    adapter_id: str
    operations: tuple[AdapterOperation, ...]
    limitations: tuple[str, ...]
    conflicts: tuple[str, ...]

    def __init__(
        self,
        *,
        adapter_id: str,
        operations: Iterable[AdapterOperation],
        limitations: Iterable[str] = (),
        conflicts: Iterable[str] = (),
    ) -> None:
        ordered_operations = tuple(
            sorted(
                operations,
                key=lambda operation: (
                    operation.path,
                    operation.ownership.value,
                    operation.intent.value,
                ),
            )
        )
        object.__setattr__(self, "adapter_id", adapter_id)
        object.__setattr__(self, "operations", ordered_operations)
        object.__setattr__(self, "limitations", tuple(limitations))
        object.__setattr__(self, "conflicts", tuple(conflicts))
