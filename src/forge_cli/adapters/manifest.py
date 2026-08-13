"""Canonical Harness Adapter manifest loading and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

import yaml
from jsonschema import ValidationError, validate

from forge_cli.protocol_resources import resolve_protocol_root


class InvalidAdapterManifestError(RuntimeError):
    code = "E_FORGE_INVALID_ADAPTER_MANIFEST"


class IncompatibleAdapterProtocolError(RuntimeError):
    code = "E_FORGE_ADAPTER_PROTOCOL_INCOMPATIBLE"

    def __init__(
        self,
        *,
        project_protocol: int,
        protocol_min: int,
        protocol_max_exclusive: int,
    ) -> None:
        self.project_protocol = project_protocol
        self.protocol_min = protocol_min
        self.protocol_max_exclusive = protocol_max_exclusive
        super().__init__(
            "Adapter does not support Forge Protocol "
            f"{project_protocol}; supported interval is "
            f"[{protocol_min}, {protocol_max_exclusive})."
        )


@dataclass(frozen=True)
class AdapterManifest:
    adapter_id: str
    version: str
    harness: str
    protocol_min: int
    protocol_max_exclusive: int
    capabilities: Mapping[str, bool]


def _adapter_schema_path() -> Path:
    return resolve_protocol_root() / "schemas" / "adapter.schema.json"


def load_adapter_manifest(path: Path) -> AdapterManifest:
    try:
        data = yaml.safe_load(path.read_text())
        schema = json.loads(_adapter_schema_path().read_text())
        validate(instance=data, schema=schema)
    except (OSError, yaml.YAMLError, json.JSONDecodeError, ValidationError, TypeError) as error:
        raise InvalidAdapterManifestError(str(error)) from error

    protocol_min = data["protocol"]["min"]
    protocol_max_exclusive = data["protocol"]["max_exclusive"]
    if protocol_min >= protocol_max_exclusive:
        raise InvalidAdapterManifestError(
            "Adapter protocol interval must satisfy min < max_exclusive."
        )

    return AdapterManifest(
        adapter_id=data["adapter"]["id"],
        version=data["adapter"]["version"],
        harness=data["adapter"]["harness"],
        protocol_min=protocol_min,
        protocol_max_exclusive=protocol_max_exclusive,
        capabilities=MappingProxyType(dict(data["capabilities"])),
    )


def is_protocol_compatible(manifest: AdapterManifest, project_protocol: int) -> bool:
    return manifest.protocol_min <= project_protocol < manifest.protocol_max_exclusive


def require_protocol_compatibility(
    manifest: AdapterManifest,
    project_protocol: int,
) -> None:
    if is_protocol_compatible(manifest, project_protocol):
        return

    raise IncompatibleAdapterProtocolError(
        project_protocol=project_protocol,
        protocol_min=manifest.protocol_min,
        protocol_max_exclusive=manifest.protocol_max_exclusive,
    )
