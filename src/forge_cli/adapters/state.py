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
        object.__setattr__(
            self,
            "generated_artifacts",
            tuple(sorted(generated_artifacts, key=lambda artifact: artifact.path)),
        )
        object.__setattr__(self, "limitations", tuple(sorted(limitations)))


def _schema() -> dict:
    path = resolve_protocol_root() / "schemas" / "adapter-installation.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _payload(record: AdapterInstallationRecord) -> dict:
    return {
        "schema": "forge/adapter-installation@1",
        "adapter": {
            "id": record.adapter_id,
            "version": record.adapter_version,
            "harness": record.harness,
        },
        "protocol": {
            "min": record.protocol_min,
            "max_exclusive": record.protocol_max_exclusive,
        },
        "generated_artifacts": [
            {"path": artifact.path, "digest": artifact.digest}
            for artifact in record.generated_artifacts
        ],
        "limitations": list(record.limitations),
    }


def write_installation_record(path: Path, record: AdapterInstallationRecord) -> None:
    payload = _payload(record)
    try:
        validate(instance=payload, schema=_schema())
    except ValidationError as exc:
        raise InvalidAdapterInstallationRecordError(exc.message) from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def load_installation_record(path: Path) -> AdapterInstallationRecord:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        validate(instance=payload, schema=_schema())
        protocol = payload["protocol"]
        return AdapterInstallationRecord(
            adapter_id=payload["adapter"]["id"],
            adapter_version=payload["adapter"]["version"],
            harness=payload["adapter"]["harness"],
            protocol_min=protocol["min"],
            protocol_max_exclusive=protocol["max_exclusive"],
            generated_artifacts=(
                GeneratedArtifact(path=item["path"], digest=item["digest"])
                for item in payload["generated_artifacts"]
            ),
            limitations=payload["limitations"],
        )
    except (OSError, TypeError, KeyError, ValidationError, yaml.YAMLError) as exc:
        message = exc.message if isinstance(exc, ValidationError) else str(exc)
        raise InvalidAdapterInstallationRecordError(message) from exc
