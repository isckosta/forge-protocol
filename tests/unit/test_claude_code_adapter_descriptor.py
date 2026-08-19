from __future__ import annotations

import importlib
import importlib.util


def _claude_code_module():
    module_spec = importlib.util.find_spec("forge_cli.adapters.claude_code")
    assert module_spec is not None, "Claude Code adapter descriptor is not implemented yet"
    return importlib.import_module("forge_cli.adapters.claude_code")


def test_claude_code_descriptor_has_stable_identity_and_protocol_interval() -> None:
    claude_code = _claude_code_module()

    descriptor = claude_code.load_claude_code_adapter_descriptor()

    assert descriptor.manifest.adapter_id == "claude-code"
    assert descriptor.manifest.harness == "claude-code"
    assert descriptor.manifest.version == "0.1.0"
    assert descriptor.manifest.protocol_min == 1
    assert descriptor.manifest.protocol_max_exclusive == 3


def test_claude_code_descriptor_claims_a_materially_richer_capability_profile_than_codex() -> None:
    """CHG-0018 discovery.md: the whole point of Claude Code as the second
    Adapter is a genuinely different capability profile from Codex's
    (skills+generated_files only)."""
    claude_code = _claude_code_module()

    capabilities = claude_code.load_claude_code_adapter_descriptor().manifest.capabilities

    assert capabilities["skills"] is True
    assert capabilities["generated_files"] is True
    assert capabilities["persistent_instructions"] is True
    assert capabilities["commands"] is True
    assert capabilities["hooks"] is True
    assert capabilities["agent_roles"] is True


def test_claude_code_capability_evidence_is_complete_and_stably_ordered() -> None:
    claude_code = _claude_code_module()

    evidence = claude_code.load_claude_code_adapter_descriptor().evidence

    assert tuple(item.capability for item in evidence) == tuple(
        sorted(item.capability for item in evidence)
    )
    assert {item.capability for item in evidence} == {
        "agent_roles",
        "commands",
        "generated_files",
        "hooks",
        "persistent_instructions",
        "skills",
    }
    for item in evidence:
        assert item.status == "supported"
        assert item.source.startswith("https://code.claude.com/docs/")
        assert item.observed_on == "2026-08-19"
