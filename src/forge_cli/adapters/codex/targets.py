from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from importlib.resources import files
from pathlib import PurePosixPath

import yaml

from forge_cli.adapters.configuration import AdapterConfiguration, resolve_configured_target


class PublicationTargetSource(StrEnum):
    EXPLICIT = "explicit"
    CONFIGURATION = "configuration"
    EVIDENCE = "evidence"


@dataclass(frozen=True)
class PublicationTarget:
    root: str
    source: PublicationTargetSource

    @property
    def path(self) -> str:
        return self.root


def _checked(path: str) -> str:
    if not path or path.startswith("~") or "\\" in path or ":" in path or "\0" in path:
        raise ValueError()
    item = PurePosixPath(path)
    if item.is_absolute() or ".." in item.parts:
        raise ValueError()
    value = item.as_posix()
    if value in {"", "."} or value == ".codex" or value.startswith(".codex/"):
        raise ValueError()
    return value


def load_packaged_publication_target() -> str:
    resource = files("forge_cli.adapters.codex").joinpath("resources", "publication.yml")
    try:
        data = yaml.safe_load(resource.read_text(encoding="utf-8"))
        target = data["target"]
        source = data["source"]
        observed_on = data["observed_on"]
    except (AttributeError, KeyError, TypeError, yaml.YAMLError) as exc:
        raise ValueError("Invalid packaged Codex publication evidence.") from exc
    if not isinstance(source, str) or not source.startswith("https://") or not observed_on:
        raise ValueError("Invalid packaged Codex publication evidence.")
    return _checked(target)


def resolve_publication_target(
    *,
    explicit_target: str | None = None,
    configuration: AdapterConfiguration | None = None,
    evidence_target: str | None = None,
) -> PublicationTarget | None:
    target = resolve_configured_target(explicit_target, configuration, evidence_target)
    if target is None:
        return None
    if explicit_target is not None:
        source = PublicationTargetSource.EXPLICIT
    elif configuration is not None and configuration.target is not None:
        source = PublicationTargetSource.CONFIGURATION
    else:
        source = PublicationTargetSource.EVIDENCE
    return PublicationTarget(_checked(target), source)


def resolve_resource_path(target: PublicationTarget, resource_name: str) -> str:
    resource = _checked(resource_name)
    return (PurePosixPath(target.root) / resource).as_posix()
