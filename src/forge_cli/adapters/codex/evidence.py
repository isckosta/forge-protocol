from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files

import yaml


@dataclass(frozen=True, order=True)
class CapabilityEvidence:
    capability: str
    status: str
    source: str
    observed_on: str


def parse_codex_capability_evidence(content: str) -> tuple[CapabilityEvidence, ...]:
    data = yaml.safe_load(content) or {}
    raw_items = data.get("evidence")
    if not isinstance(raw_items, list):
        raise ValueError("Codex capability evidence must contain an evidence list.")

    items: list[CapabilityEvidence] = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            raise ValueError("Codex capability evidence entries must be mappings.")
        try:
            capability = str(raw["capability"])
            status = str(raw["status"])
            source = str(raw["source"])
            observed = raw["observed_on"]
        except KeyError as exc:
            raise ValueError(f"Missing Codex capability evidence field: {exc.args[0]}") from exc

        observed_on = observed.isoformat() if hasattr(observed, "isoformat") else str(observed)
        if not capability or status not in {"supported", "unsupported"} or not source or not observed_on:
            raise ValueError("Invalid Codex capability evidence entry.")
        items.append(CapabilityEvidence(capability, status, source, observed_on))

    return tuple(sorted(items, key=lambda item: item.capability))


def load_packaged_codex_evidence() -> tuple[CapabilityEvidence, ...]:
    resource = files("forge_cli.adapters.codex").joinpath("resources", "capabilities.yml")
    return parse_codex_capability_evidence(resource.read_text(encoding="utf-8"))
