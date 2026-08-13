from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath


class PublicationTargetSource(StrEnum):
    EXPLICIT = "explicit"
    EVIDENCE = "evidence"


@dataclass(frozen=True)
class PublicationTarget:
    root: str
    source: PublicationTargetSource

    @property
    def path(self) -> str:
        return self.root


def _checked(path: str) -> str:
    if not path or "\\" in path:
        raise ValueError()
    item = PurePosixPath(path)
    if item.is_absolute() or ".." in item.parts:
        raise ValueError()
    value = item.as_posix()
    if value in {"", "."}:
        raise ValueError()
    return value


def resolve_publication_target(
    *,
    explicit_target: str | None = None,
    evidence_target: str | None = None,
) -> PublicationTarget | None:
    if explicit_target is not None:
        return PublicationTarget(_checked(explicit_target), PublicationTargetSource.EXPLICIT)
    if evidence_target is not None:
        return PublicationTarget(_checked(evidence_target), PublicationTargetSource.EVIDENCE)
    return None


def resolve_resource_path(target: PublicationTarget, resource_name: str) -> str:
    resource = _checked(resource_name)
    return (PurePosixPath(target.root) / resource).as_posix()
