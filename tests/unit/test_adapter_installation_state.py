import importlib
from pathlib import Path

import pytest
import yaml


def state_module():
    try:
        return importlib.import_module("forge_cli.adapters.state")
    except ModuleNotFoundError:
        pytest.fail("Adapter installation state is not implemented yet")


def test_installation_record_round_trips_deterministically(tmp_path: Path) -> None:
    module = state_module()
    record = module.AdapterInstallationRecord(
        adapter_id="cursor",
        adapter_version="1.2.3",
        harness="cursor",
        protocol_min=1,
        protocol_max_exclusive=2,
        publication_root=".cursor",
        generated_artifacts=(
            module.GeneratedArtifact(path=".cursor/rules/forge.md", digest="b" * 64),
            module.GeneratedArtifact(path=".cursor/commands/forge.md", digest="a" * 64),
        ),
        limitations=("hooks unavailable", "agent roles unavailable"),
    )

    path = tmp_path / ".forge" / "adapters" / "cursor" / "installation.yml"
    module.write_installation_record(path, record)
    first = path.read_text(encoding="utf-8")
    loaded = module.load_installation_record(path)
    module.write_installation_record(path, loaded)
    second = path.read_text(encoding="utf-8")

    assert loaded == record
    assert yaml.safe_load(first)["schema"] == "forge/adapter-installation@2"
    assert loaded.publication_root == ".cursor"
    assert first == second
    assert [artifact.path for artifact in loaded.generated_artifacts] == [
        ".cursor/commands/forge.md",
        ".cursor/rules/forge.md",
    ]


def test_installation_record_contains_only_derived_adapter_state(tmp_path: Path) -> None:
    module = state_module()
    record = module.AdapterInstallationRecord(
        adapter_id="codex",
        adapter_version="0.1.0",
        harness="codex",
        protocol_min=1,
        protocol_max_exclusive=2,
        publication_root=".agents/skills/forge",
        generated_artifacts=(),
        limitations=(),
    )
    path = tmp_path / "installation.yml"

    module.write_installation_record(path, record)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))

    forbidden = {"change", "state", "stage", "status", "tdd", "verification", "review", "completion"}
    assert forbidden.isdisjoint(payload.keys())
    assert set(payload.keys()) == {
        "schema",
        "adapter",
        "protocol",
        "publication",
        "generated_artifacts",
        "limitations",
    }
    assert payload["publication"] == {"root": ".agents/skills/forge"}


def test_loading_legacy_record_preserves_missing_publication_ownership(
    tmp_path: Path,
) -> None:
    module = state_module()
    path = tmp_path / "installation.yml"
    path.write_text(
        """schema: forge/adapter-installation@1
adapter:
  id: codex
  version: 0.0.9
  harness: codex
protocol:
  min: 1
  max_exclusive: 2
generated_artifacts: []
limitations: []
""",
        encoding="utf-8",
    )

    record = module.load_installation_record(path)

    assert record.publication_root is None


def test_loading_rejects_change_lifecycle_fields(tmp_path: Path) -> None:
    module = state_module()
    path = tmp_path / "installation.yml"
    path.write_text(
        """schema: forge/adapter-installation@1
adapter:
  id: cursor
  version: 1.0.0
  harness: cursor
protocol:
  min: 1
  max_exclusive: 2
generated_artifacts: []
limitations: []
review:
  status: passed
""",
        encoding="utf-8",
    )

    with pytest.raises(module.InvalidAdapterInstallationRecordError):
        module.load_installation_record(path)


def test_loading_rejects_invalid_generated_artifact_digest(tmp_path: Path) -> None:
    module = state_module()
    path = tmp_path / "installation.yml"
    path.write_text(
        """schema: forge/adapter-installation@1
adapter:
  id: cursor
  version: 1.0.0
  harness: cursor
protocol:
  min: 1
  max_exclusive: 2
generated_artifacts:
  - path: .cursor/rules/forge.md
    digest: not-a-sha256
limitations: []
""",
        encoding="utf-8",
    )

    with pytest.raises(module.InvalidAdapterInstallationRecordError):
        module.load_installation_record(path)
