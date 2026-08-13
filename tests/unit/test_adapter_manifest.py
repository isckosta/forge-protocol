from __future__ import annotations

import importlib
from pathlib import Path

import pytest


VALID_MANIFEST = """\
schema: forge/adapter@1
adapter:
  id: example
  version: 0.1.0
  harness: example-harness
protocol:
  min: 1
  max_exclusive: 2
capabilities:
  persistent_instructions: true
  commands: false
  skills: true
  hooks: false
  agent_roles: false
  generated_files: true
"""


def write_manifest(tmp_path: Path, content: str = VALID_MANIFEST) -> Path:
    path = tmp_path / "adapter.yml"
    path.write_text(content)
    return path


def manifest_module():
    return importlib.import_module("forge_cli.adapters.manifest")


def test_loads_canonical_adapter_manifest(tmp_path: Path) -> None:
    module = manifest_module()

    manifest = module.load_adapter_manifest(write_manifest(tmp_path))

    assert manifest.adapter_id == "example"
    assert manifest.version == "0.1.0"
    assert manifest.harness == "example-harness"
    assert manifest.protocol_min == 1
    assert manifest.protocol_max_exclusive == 2
    assert manifest.capabilities == {
        "persistent_instructions": True,
        "commands": False,
        "skills": True,
        "hooks": False,
        "agent_roles": False,
        "generated_files": True,
    }


def test_rejects_manifest_with_unknown_capability(tmp_path: Path) -> None:
    module = manifest_module()
    invalid = VALID_MANIFEST.replace(
        "  generated_files: true",
        "  generated_files: true\n  teleportation: true",
    )

    with pytest.raises(module.InvalidAdapterManifestError) as error:
        module.load_adapter_manifest(write_manifest(tmp_path, invalid))

    assert error.value.code == "E_FORGE_INVALID_ADAPTER_MANIFEST"


def test_rejects_manifest_missing_required_identity(tmp_path: Path) -> None:
    module = manifest_module()
    invalid = VALID_MANIFEST.replace("  harness: example-harness\n", "")

    with pytest.raises(module.InvalidAdapterManifestError):
        module.load_adapter_manifest(write_manifest(tmp_path, invalid))


def test_rejects_non_integer_protocol_bounds(tmp_path: Path) -> None:
    module = manifest_module()
    invalid = VALID_MANIFEST.replace("  min: 1", "  min: '1'")

    with pytest.raises(module.InvalidAdapterManifestError):
        module.load_adapter_manifest(write_manifest(tmp_path, invalid))
