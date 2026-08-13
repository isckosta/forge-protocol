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

    return AdapterManifest(
        adapter_id=data["adapter"]["id"],
        version=data["adapter"]["version"],
        harness=data["adapter"]["harness"],
        protocol_min=data["protocol"]["min"],
        protocol_max_exclusive=data["protocol"]["max_exclusive"],
        capabilities=MappingProxyType(dict(data["capabilities"])),
    )
