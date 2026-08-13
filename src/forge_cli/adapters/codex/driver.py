"""Codex implementation of the generic Harness Driver contract."""

from __future__ import annotations

from dataclasses import dataclass

from forge_cli.adapters.codex.descriptor import load_codex_adapter_descriptor
from forge_cli.adapters.driver import (
    AdapterProjection,
    AdapterProjectionContext,
)
from forge_cli.adapters.manifest import AdapterManifest


@dataclass(frozen=True)
class CodexDriver:
    @property
    def manifest(self) -> AdapterManifest:
        return load_codex_adapter_descriptor().manifest

    @property
    def default_target(self) -> str | None:
        return None

    def project(self, context: AdapterProjectionContext) -> AdapterProjection:
        raise NotImplementedError
