from pathlib import Path
import tempfile

from forge_cli.adapters.manifest import load_adapter_manifest
from forge_cli.adapters.state import (
    AdapterInstallationRecord,
    GeneratedArtifact,
    load_installation_record,
    write_installation_record,
)
from forge_cli.protocol_resources import resolve_protocol_root


protocol_root = resolve_protocol_root()
assert (protocol_root / "schemas" / "adapter.schema.json").is_file()
assert (protocol_root / "schemas" / "adapter-installation.schema.json").is_file()

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    manifest_path = root / "adapter.yml"
    manifest_path.write_text(
        "\n".join(
            [
                "schema: forge/adapter@1",
                "adapter:",
                "  id: example",
                "  version: 1.0.0",
                "  harness: example",
                "protocol:",
                "  min: 1",
                "  max_exclusive: 2",
                "capabilities:",
                "  persistent_instructions: true",
                "  commands: true",
                "  skills: true",
                "  hooks: false",
                "  agent_roles: false",
                "  generated_files: true",
                "",
            ]
        ),
        encoding="utf-8",
    )
    assert load_adapter_manifest(manifest_path).adapter_id == "example"

    installation_path = root / "installation.yml"
    record = AdapterInstallationRecord(
        adapter_id="example",
        adapter_version="1.0.0",
        harness="example",
        protocol_min=1,
        protocol_max_exclusive=2,
        generated_artifacts=(
            GeneratedArtifact(path="generated.md", digest="a" * 64),
        ),
        limitations=(),
    )
    write_installation_record(installation_path, record)
    assert load_installation_record(installation_path) == record

print("Adapter isolated wheel probe passed")
