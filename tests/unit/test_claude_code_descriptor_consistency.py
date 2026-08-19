from importlib.resources import files

import yaml

from forge_cli.adapters.claude_code import load_claude_code_adapter_descriptor


def test_packaged_manifest_fully_matches_runtime_descriptor():
    data = yaml.safe_load(
        files("forge_cli.adapters.claude_code").joinpath("resources", "adapter.yml").read_text(encoding="utf-8")
    )
    manifest = load_claude_code_adapter_descriptor().manifest
    assert manifest.harness == data["adapter"]["harness"]
    assert manifest.protocol_min == data["protocol"]["min"]
    assert manifest.protocol_max_exclusive == data["protocol"]["max_exclusive"]
    assert dict(manifest.capabilities) == data["capabilities"]


def test_packaged_evidence_fully_matches_runtime_descriptor():
    data = yaml.safe_load(
        files("forge_cli.adapters.claude_code").joinpath("resources", "capabilities.yml").read_text(encoding="utf-8")
    )
    descriptor = load_claude_code_adapter_descriptor()
    packaged = sorted((x["capability"], x["status"], x["source"], str(x["observed_on"])) for x in data["evidence"])
    runtime = sorted((x.capability, x.status, x.source, x.observed_on) for x in descriptor.evidence)
    assert runtime == packaged
