from __future__ import annotations

from pathlib import Path

import pytest

from forge_cli.adapters import manifest as adapter_manifest


MANIFEST = """\
schema: forge/adapter@1
adapter:
  id: example
  version: 0.1.0
  harness: example-harness
protocol:
  min: 1
  max_exclusive: 3
capabilities:
  persistent_instructions: true
  commands: false
  skills: true
  hooks: false
  agent_roles: false
  generated_files: true
"""


def load(tmp_path: Path, content: str = MANIFEST):
    path = tmp_path / "adapter.yml"
    path.write_text(content)
    return adapter_manifest.load_adapter_manifest(path)


def test_protocol_interval_is_half_open(tmp_path: Path) -> None:
    manifest = load(tmp_path)

    assert adapter_manifest.is_protocol_compatible(manifest, 1) is True
    assert adapter_manifest.is_protocol_compatible(manifest, 2) is True
    assert adapter_manifest.is_protocol_compatible(manifest, 3) is False
    assert adapter_manifest.is_protocol_compatible(manifest, 0) is False


def test_require_protocol_compatibility_rejects_outside_interval(tmp_path: Path) -> None:
    manifest = load(tmp_path)

    with pytest.raises(adapter_manifest.IncompatibleAdapterProtocolError) as error:
        adapter_manifest.require_protocol_compatibility(manifest, 3)

    assert error.value.code == "E_FORGE_ADAPTER_PROTOCOL_INCOMPATIBLE"
    assert error.value.project_protocol == 3
    assert error.value.protocol_min == 1
    assert error.value.protocol_max_exclusive == 3


def test_require_protocol_compatibility_accepts_supported_protocol(tmp_path: Path) -> None:
    manifest = load(tmp_path)

    adapter_manifest.require_protocol_compatibility(manifest, 2)


def test_rejects_empty_or_reversed_protocol_interval(tmp_path: Path) -> None:
    invalid = MANIFEST.replace("  min: 1\n  max_exclusive: 3", "  min: 3\n  max_exclusive: 3")

    with pytest.raises(adapter_manifest.InvalidAdapterManifestError):
        load(tmp_path, invalid)
