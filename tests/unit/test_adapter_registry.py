from __future__ import annotations

import socket
from dataclasses import dataclass

import pytest

from forge_cli.adapters.driver import AdapterProjectionContext
from forge_cli.adapters.manifest import AdapterManifest
from forge_cli.adapters.codex.driver import CodexDriver
from forge_cli.adapters.packaged import build_packaged_registry
from forge_cli.adapters.registry import (
    AdapterRegistry,
    DuplicateAdapterError,
    UnknownAdapterError,
)


@dataclass(frozen=True)
class _Driver:
    manifest: AdapterManifest
    default_target: str | None = None

    def project(self, context: object) -> object:
        raise NotImplementedError


def _driver(adapter_id: str) -> _Driver:
    return _Driver(
        manifest=AdapterManifest(
            adapter_id=adapter_id,
            version="1.0.0",
            harness=adapter_id,
            protocol_min=1,
            protocol_max_exclusive=2,
            capabilities={},
        )
    )


def test_registry_orders_drivers_by_adapter_id() -> None:
    registry = AdapterRegistry((_driver("zeta"), _driver("alpha")))

    assert [item.manifest.adapter_id for item in registry.list()] == ["alpha", "zeta"]


def test_registry_rejects_unknown_adapter_with_stable_code() -> None:
    registry = AdapterRegistry((_driver("alpha"),))

    with pytest.raises(UnknownAdapterError) as error:
        registry.get("missing")
    assert error.value.code == "E_FORGE_ADAPTER_UNKNOWN"


def test_registry_rejects_duplicate_adapter_ids() -> None:
    with pytest.raises(DuplicateAdapterError):
        AdapterRegistry((_driver("codex"), _driver("codex")))


def test_packaged_registry_contains_codex_without_network(monkeypatch) -> None:
    monkeypatch.setattr(
        socket,
        "create_connection",
        lambda *args, **kwargs: pytest.fail("network"),
    )

    assert build_packaged_registry().get("codex").manifest.harness == "codex"


def test_codex_driver_exposes_packaged_manifest() -> None:
    driver = CodexDriver()

    assert driver.manifest.adapter_id == "codex"
    assert driver.manifest.harness == "codex"


def test_codex_driver_projects_empty_effective_flow_set_as_a_skill() -> None:
    context = AdapterProjectionContext(
        project_protocol=1,
        flows=(),
        contract_content="contract",
        target=".agents/skills/forge",
    )

    projection = CodexDriver().project(context)

    assert [artifact.path for artifact in projection.artifacts] == [
        ".agents/skills/forge/SKILL.md",
        ".agents/skills/forge/references/engineering-contract.md",
    ]
