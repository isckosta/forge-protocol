from __future__ import annotations

import importlib
import pytest


def _load(name: str):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        pytest.fail(f"Missing runtime resource loader: {name}")


def test_manifest_parser_uses_resource_content() -> None:
    module = _load("forge_cli.adapters.codex.descriptor")
    manifest = module.parse_codex_adapter_manifest(
        "schema: forge/adapter@1\nadapter: {id: codex-test, version: 9.9.9, harness: codex}\nprotocol: {min: 3, max_exclusive: 7}\ncapabilities: {persistent_instructions: false, commands: false, skills: true, hooks: false, agent_roles: false, generated_files: true}\n"
    )
    assert manifest.adapter_id == "codex-test"
    assert manifest.version == "9.9.9"
    assert (manifest.protocol_min, manifest.protocol_max_exclusive) == (3, 7)


def test_evidence_parser_uses_resource_content() -> None:
    module = _load("forge_cli.adapters.codex.evidence")
    items = module.parse_codex_capability_evidence(
        "evidence:\n  - capability: skills\n    status: supported\n    source: docs\n    observed_on: 2030-01-02\n"
    )
    assert [(item.capability, item.status, item.source, item.observed_on) for item in items] == [
        ("skills", "supported", "docs", "2030-01-02")
    ]
