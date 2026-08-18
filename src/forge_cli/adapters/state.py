"""Repository-native derived installation state for Harness Adapters."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from jsonschema import ValidationError, validate
import yaml

from forge_cli.protocol_resources import resolve_protocol_root


class InvalidAdapterInstallationRecordError(ValueError):
    """Raised when Adapter installation metadata violates the canonical schema."""


@dataclass(frozen=True, order=True)
class GeneratedArtifact:
    path: str
    digest: str


@dataclass(frozen=True)
class AdapterInstallationRecord:
    adapter_id: str
    adapter_version: str
    harness: str
    protocol_min: int
    protocol_max_exclusive: int
    publication_root: str | None
    generated_artifacts: tuple[GeneratedArtifact, ...]
    limitations: tuple[str, ...]

    def __init__(
        self,
        *,
        adapter_id: str,
        adapter_version: str,
        harness: str,
        protocol_min: int,
        protocol_max_exclusive: int,
        generated_artifacts: Iterable[GeneratedArtifact],
        limitations: Iterable[str],
        publication_root: str | None = None,
    ) -> None:
        if protocol_min >= protocol_max_exclusive:
            raise InvalidAdapterInstallationRecordError(
                "Adapter installation Protocol interval must satisfy min < max_exclusive."
            )
        object.__setattr__(self, "adapter_id", adapter_id)
        object.__setattr__(self, "adapter_version", adapter_version)
        object.__setattr__(self, "harness", harness)
        object.__setattr__(self, "protocol_min", protocol_min)
        object.__setattr__(self, "protocol_max_exclusive", protocol_max_exclusive)
        object.__setattr__(self, "publication_root", publication_root)
        object.__setattr__(
            self,
            "generated_artifacts",
            tuple(sorted(generated_artifacts, key=lambda artifact: artifact.path)),
        )
        object.__setattr__(self, "limitations", tuple(sorted(limitations)))


def _schema(identifier: str) -> dict:
    filenames = {
        "forge/adapter-installation@1": "adapter-installation.schema.json",
        "forge/adapter-installation@2": "adapter-installation-v2.schema.json",
    }
    try:
        filename = filenames[identifier]
    except KeyError as exc:
        raise InvalidAdapterInstallationRecordError(
            f"Unsupported Adapter installation record schema: {identifier!r}."
        ) from exc
    path = resolve_protocol_root() / "schemas" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _payload(record: AdapterInstallationRecord) -> dict:
    schema = (
        "forge/adapter-installation@2"
        if record.publication_root is not None
        else "forge/adapter-installation@1"
    )
    payload: dict = {
        "schema": schema,
        "adapter": {
            "id": record.adapter_id,
            "version": record.adapter_version,
            "harness": record.harness,
        },
        "protocol": {
            "min": record.protocol_min,
            "max_exclusive": record.protocol_max_exclusive,
        },
    }
    if record.publication_root is not None:
        payload["publication"] = {"root": record.publication_root}
    payload["generated_artifacts"] = [
        {"path": artifact.path, "digest": artifact.digest}
        for artifact in record.generated_artifacts
    ]
    payload["limitations"] = list(record.limitations)
    return payload


def write_installation_record(path: Path, record: AdapterInstallationRecord) -> None:
    payload = _payload(record)
    try:
        validate(instance=payload, schema=_schema(payload["schema"]))
    except ValidationError as exc:
        raise InvalidAdapterInstallationRecordError(exc.message) from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def parse_installation_record(text: str) -> AdapterInstallationRecord:
    """Parse an installation record from already-read text.

    Callers that must derive a validation/authorization decision and a
    rollback backup from the exact same on-disk content should read the file
    once and pass that text here, instead of calling load_installation_record
    (which performs its own file read) after a separate read of their own --
    two physical reads of the same path give a concurrent writer a window to
    change the content in between, desynchronizing what was authorized from
    what gets restored on rollback.
    """
    try:
        payload = yaml.safe_load(text)
        if not isinstance(payload, dict):
            raise InvalidAdapterInstallationRecordError(
                "Adapter installation record must be a mapping."
            )
        validate(instance=payload, schema=_schema(payload.get("schema")))
        protocol = payload["protocol"]
        publication = payload.get("publication")
        return AdapterInstallationRecord(
            adapter_id=payload["adapter"]["id"],
            adapter_version=payload["adapter"]["version"],
            harness=payload["adapter"]["harness"],
            protocol_min=protocol["min"],
            protocol_max_exclusive=protocol["max_exclusive"],
            publication_root=(
                publication["root"] if publication is not None else None
            ),
            generated_artifacts=(
                GeneratedArtifact(path=item["path"], digest=item["digest"])
                for item in payload["generated_artifacts"]
            ),
            limitations=payload["limitations"],
        )
    except (
        TypeError,
        KeyError,
        ValidationError,
        yaml.YAMLError,
    ) as exc:
        message = exc.message if isinstance(exc, ValidationError) else str(exc)
        raise InvalidAdapterInstallationRecordError(message) from exc


def load_installation_record(path: Path) -> AdapterInstallationRecord:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InvalidAdapterInstallationRecordError(str(exc)) from exc
    return parse_installation_record(text)
