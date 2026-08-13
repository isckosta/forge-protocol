from __future__ import annotations

import importlib
import importlib.util


def _codex_module():
    module_spec = importlib.util.find_spec("forge_cli.adapters.codex")
    assert module_spec is not None, "Codex adapter descriptor is not implemented yet"
    return importlib.import_module("forge_cli.adapters.codex")


def test_codex_descriptor_has_stable_identity_and_protocol_interval() -> None:
    codex = _codex_module()

    descriptor = codex.load_codex_adapter_descriptor()

    assert descriptor.manifest.adapter_id == "codex"
    assert descriptor.manifest.harness == "codex"
    assert descriptor.manifest.version == "0.1.0"
    assert descriptor.manifest.protocol_min == 1
    assert descriptor.manifest.protocol_max_exclusive == 2


def test_codex_descriptor_only_claims_evidence_backed_initial_capabilities() -> None:
    codex = _codex_module()

    capabilities = codex.load_codex_adapter_descriptor().manifest.capabilities

    assert capabilities["skills"] is True
    assert capabilities["generated_files"] is True
    assert capabilities["persistent_instructions"] is False
    assert capabilities["commands"] is False
    assert capabilities["hooks"] is False
    assert capabilities["agent_roles"] is False


def test_codex_capability_evidence_is_complete_and_stably_ordered() -> None:
    codex = _codex_module()

    evidence = codex.load_codex_adapter_descriptor().evidence

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
        assert item.status in {"supported", "unsupported"}
        assert item.source
        assert item.observed_on == "2026-08-13"


def test_codex_evidence_does_not_claim_support_for_unverified_primitives() -> None:
    codex = _codex_module()

    evidence_by_capability = {
        item.capability: item for item in codex.load_codex_adapter_descriptor().evidence
    }

    assert evidence_by_capability["skills"].status == "supported"
    assert evidence_by_capability["generated_files"].status == "supported"
    for capability in (
        "persistent_instructions",
        "commands",
        "hooks",
        "agent_roles",
    ):
        assert evidence_by_capability[capability].status == "unsupported"
