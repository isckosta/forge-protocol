"""Forge project configuration boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import ValidationError, validate


SUPPORTED_PROTOCOLS = {1}


class InvalidProjectConfigurationError(RuntimeError):
    code = "E_FORGE_INVALID_PROJECT_CONFIGURATION"


class UnsupportedProtocolVersionError(RuntimeError):
    code = "E_FORGE_UNSUPPORTED_PROTOCOL"

    def __init__(self, protocol: object) -> None:
        self.protocol = protocol
        super().__init__(f"Unsupported Forge Protocol version: {protocol}")


def _project_schema_path() -> Path:
    return Path(__file__).resolve().parents[3] / "protocol" / "schemas" / "project.schema.json"


def load_project_configuration(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text())
        schema = json.loads(_project_schema_path().read_text())
        validate(instance=data, schema=schema)
    except (OSError, yaml.YAMLError, json.JSONDecodeError, ValidationError, TypeError) as error:
        raise InvalidProjectConfigurationError(str(error)) from error

    protocol = data["forge"]["protocol"]
    if protocol not in SUPPORTED_PROTOCOLS:
        raise UnsupportedProtocolVersionError(protocol)

    return data
