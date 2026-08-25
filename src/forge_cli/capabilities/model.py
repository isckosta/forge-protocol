"""Minimal model for a Forge Capability definition loaded from CAPABILITY.md."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Capability:
    id: str
    schema: int
    identity: str
    purpose: str
    applicability: str
    inputs: str
    behavior: str
    outputs: str
    evidence_expectations: str
    source_path: Path
