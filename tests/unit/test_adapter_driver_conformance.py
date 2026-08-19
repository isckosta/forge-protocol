"""Shared conformance suite (CHG-0018 FR-008/C-074): assertions every
Harness Driver must satisfy, run against both concrete Adapters. This is
new — no prior Change ever exercised more than one Harness Driver against
the same assertions."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from forge_cli.adapters.claude_code.driver import ClaudeCodeDriver
from forge_cli.adapters.codex.driver import CodexDriver
from forge_cli.adapters.driver import AdapterProjectionContext
from forge_cli.adapters.manifest import is_protocol_compatible

FLOW = """schema: forge/flow@1
flow:
  id: standard
stages:
  - id: tdd_implementation
  - id: verification
  - id: strict_review
gates:
  before_behavioral_implementation:
    checks: [red_executed, red_failed_for_expected_reason]
"""

DRIVERS = pytest.mark.parametrize("driver", [CodexDriver(), ClaudeCodeDriver()], ids=["codex", "claude-code"])


@DRIVERS
def test_manifest_declares_a_valid_half_open_protocol_interval(driver) -> None:
    manifest = driver.manifest
    assert manifest.protocol_min < manifest.protocol_max_exclusive
    assert is_protocol_compatible(manifest, manifest.protocol_min)
    assert not is_protocol_compatible(manifest, manifest.protocol_max_exclusive)


@DRIVERS
def test_manifest_declares_exactly_the_six_canonical_capabilities(driver) -> None:
    """protocol/specification.md SS34: capability vocabulary is fixed."""
    assert set(driver.manifest.capabilities) == {
        "persistent_instructions",
        "commands",
        "skills",
        "hooks",
        "agent_roles",
        "generated_files",
    }
    assert all(isinstance(value, bool) for value in driver.manifest.capabilities.values())


@DRIVERS
def test_default_target_passes_its_own_validation(driver) -> None:
    target = driver.default_target
    assert target is not None
    driver.validate_publication_root(target)  # must not raise


@DRIVERS
def test_projection_is_deterministic(driver) -> None:
    context = AdapterProjectionContext(
        project_protocol=driver.manifest.protocol_min,
        flows=(("standard", FLOW),),
        contract_content="# Engineering Contract\nCanonical contract text.\n",
        target=driver.default_target,
    )

    first = driver.project(context)
    second = driver.project(context)

    assert first == second


@DRIVERS
def test_every_projected_artifact_is_a_strict_descendant_of_the_target(driver) -> None:
    """ownership.require_publication_root_ownership's own invariant,
    checked directly against each driver's real output."""
    context = AdapterProjectionContext(
        project_protocol=driver.manifest.protocol_min,
        flows=(("standard", FLOW),),
        contract_content="contract",
        target=driver.default_target,
    )

    projection = driver.project(context)
    root = PurePosixPath(driver.default_target)

    for artifact in projection.artifacts:
        path = PurePosixPath(artifact.path)
        assert root in path.parents, f"{artifact.path!r} escapes publication root {driver.default_target!r}"


@DRIVERS
def test_projection_preserves_repository_semantic_authority(driver) -> None:
    """protocol/specification.md SS36: Harness representation MUST
    preserve repository semantic authority."""
    context = AdapterProjectionContext(
        project_protocol=driver.manifest.protocol_min,
        flows=(("standard", FLOW),),
        contract_content="contract",
        target=driver.default_target,
    )

    projection = driver.project(context)

    assert projection.representation.repository_authority_preserved is True


@DRIVERS
def test_projection_never_claims_enforcement_it_cannot_technically_prove(driver) -> None:
    """Neither Adapter's TDD/Strict-Review representation is reported as
    ENFORCED via the `skills` capability alone -- both are REPRESENTED,
    surfaced as explicit CapabilityLimitations, matching C-066/C-073's
    honesty discipline for every Harness, not just one."""
    context = AdapterProjectionContext(
        project_protocol=driver.manifest.protocol_min,
        flows=(("standard", FLOW),),
        contract_content="contract",
        target=driver.default_target,
    )

    projection = driver.project(context)
    limitation_ids = {item.requirement_id for item in projection.limitations}

    assert {"strict-review", "tdd-red-before-behavior"} <= limitation_ids
    assert all(not limitation.enforced for limitation in projection.limitations)


def test_both_drivers_register_without_collision() -> None:
    from forge_cli.adapters.registry import AdapterRegistry

    registry = AdapterRegistry((CodexDriver(), ClaudeCodeDriver()))

    assert {driver.manifest.adapter_id for driver in registry.list()} == {"codex", "claude-code"}
