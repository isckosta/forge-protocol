"""Application composition for Harness Drivers distributed with Forge."""

from __future__ import annotations

from forge_cli.adapters.codex.driver import CodexDriver
from forge_cli.adapters.registry import AdapterRegistry


def build_packaged_registry() -> AdapterRegistry:
    return AdapterRegistry((CodexDriver(),))
