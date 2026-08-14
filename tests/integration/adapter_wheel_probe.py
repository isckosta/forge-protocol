from importlib.resources import files
import json
from pathlib import Path
import tempfile

import yaml
from jsonschema import Draft202012Validator

from forge_cli.adapters.codex import load_codex_adapter_descriptor
from forge_cli.adapters.codex.integration import (
    build_codex_installation_record,
    detect_codex_drift,
    plan_codex_projection,
)
from forge_cli.adapters.codex.projection import (
    CodexProjectionInput,
    generate_codex_projection_bundle,
)
from forge_cli.adapters.codex.targets import resolve_publication_target
from forge_cli.adapters.manifest import load_adapter_manifest
from forge_cli.adapters.state import (
    AdapterInstallationRecord,
    GeneratedArtifact,
    load_installation_record,
    write_installation_record,
)
from forge_cli.protocol_resources import resolve_protocol_root


protocol_root = resolve_protocol_root()
schema_root = protocol_root / "schemas"
catalog = yaml.safe_load((schema_root / "catalog.yml").read_text(encoding="utf-8"))
catalog_schema = json.loads(
    (schema_root / "schema-catalog.schema.json").read_text(encoding="utf-8")
)
Draft202012Validator.check_schema(catalog_schema)
Draft202012Validator(catalog_schema).validate(catalog)
cataloged_files = {entry["file"] for entry in catalog["schemas"]}
assert {path.name for path in schema_root.glob("*.schema.json")} == cataloged_files
for entry in catalog["schemas"]:
    schema = json.loads((schema_root / entry["file"]).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["properties"]["schema"]["const"] == entry["id"]

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
        publication_root=".",
        generated_artifacts=(GeneratedArtifact(path="generated.md", digest="a" * 64),),
        limitations=(),
    )
    write_installation_record(installation_path, record)
    assert load_installation_record(installation_path) == record

codex_resources = files("forge_cli.adapters.codex").joinpath("resources")
assert codex_resources.joinpath("adapter.yml").is_file()
assert codex_resources.joinpath("capabilities.yml").is_file()
assert codex_resources.joinpath("skills", "workflow.md").is_file()

descriptor = load_codex_adapter_descriptor()
assert descriptor.manifest.adapter_id == "codex"
bundle = generate_codex_projection_bundle(
    CodexProjectionInput(
        flow_id="full",
        flow_content="stages:\n  - id: verification\n",
        contract_content="canonical: true\n",
    )
)
target = resolve_publication_target(explicit_target="codex-output")
assert target is not None
plan = plan_codex_projection(
    bundle=bundle,
    target=target,
    project_protocol=1,
    capability_requirements=(),
    repository_state=(),
)
record = build_codex_installation_record(
    descriptor=descriptor,
    plan=plan,
    target=target,
)
observed = {artifact.path: artifact.digest for artifact in record.generated_artifacts}
assert detect_codex_drift(record=record, observed_digests=observed) == ()

print("Adapter isolated wheel probe passed")
