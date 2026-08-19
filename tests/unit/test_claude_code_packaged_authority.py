from __future__ import annotations

import importlib
import pytest


def _load(name: str):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        pytest.fail(f"Missing runtime resource loader: {name}")


def test_manifest_parser_uses_resource_content() -> None:
    module = _load("forge_cli.adapters.claude_code.descriptor")
    manifest = module.parse_claude_code_adapter_manifest(
        "schema: forge/adapter@1\nadapter: {id: claude-code-test, version: 9.9.9, harness: claude-code}\nprotocol: {min: 3, max_exclusive: 7}\ncapabilities: {persistent_instructions: true, commands: true, skills: true, hooks: true, agent_roles: true, generated_files: true}\n"
    )
    assert manifest.adapter_id == "claude-code-test"
    assert manifest.version == "9.9.9"
    assert (manifest.protocol_min, manifest.protocol_max_exclusive) == (3, 7)


def test_evidence_parser_uses_resource_content() -> None:
    module = _load("forge_cli.adapters.claude_code.evidence")
    items = module.parse_claude_code_capability_evidence(
        "evidence:\n  - capability: skills\n    status: supported\n    source: docs\n    observed_on: 2030-01-02\n"
    )
    assert [(item.capability, item.status, item.source, item.observed_on) for item in items] == [
        ("skills", "supported", "docs", "2030-01-02")
    ]
