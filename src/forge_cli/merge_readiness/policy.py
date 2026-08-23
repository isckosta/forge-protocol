from __future__ import annotations

from pathlib import Path

import yaml

from forge_cli.protocol_resources import resolve_protocol_root


class MaterialityPolicyError(RuntimeError):
    pass


def load_materiality_policy(protocol_root: Path | None = None) -> dict:
    root = protocol_root or resolve_protocol_root()
    path = root / "policies" / "merge-readiness.yml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise MaterialityPolicyError(f"Cannot load Merge Readiness policy: {path}") from error
    if not isinstance(data, dict) or data.get("schema") != "forge/policy/merge-readiness@1":
        raise MaterialityPolicyError(f"Invalid Merge Readiness policy: {path}")
    policy = data.get("merge_readiness")
    if not isinstance(policy, dict):
        raise MaterialityPolicyError(f"Invalid Merge Readiness policy: {path}")
    return policy


def classify_path(path: str, policy: dict | None = None) -> str:
    policy = policy or load_materiality_policy()
    if path.startswith(policy.get("change_prefix", "\0")):
        return "change"
    if path in policy.get("material_paths", []):
        return "material"
    if path in policy.get("permitted_paths", []):
        return "permitted"
    if any(path.startswith(prefix) for prefix in policy.get("ambiguous_prefixes", [])):
        return "ambiguous"
    if any(path.startswith(prefix) for prefix in policy.get("material_prefixes", [])):
        return "material"
    if any(path.startswith(prefix) for prefix in policy.get("permitted_prefixes", [])):
        return "permitted"
    return "ambiguous"
