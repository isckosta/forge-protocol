"""Safe provenance available to the local FER writer."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any
from datetime import datetime, timezone

import yaml

from forge_cli.version import CLI_VERSION


def collect_context(project_root: Path, **explicit: str | None) -> dict[str, Any]:
    context: dict[str, Any] = {
        "forge_version": CLI_VERSION,
        "repository": project_root.name,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            context["commit"] = result.stdout.strip()
    except OSError:
        pass
    configuration_path = project_root / ".forge" / "forge.yml"
    try:
        configuration = yaml.safe_load(configuration_path.read_text(encoding="utf-8")) or {}
        forge = configuration.get("forge", {})
        flows = configuration.get("flows", {})
        if isinstance(forge, dict) and "protocol" in forge:
            context["protocol"] = forge["protocol"]
        if isinstance(flows, dict) and "default" in flows:
            context["flow"] = flows["default"]
    except (OSError, yaml.YAMLError, AttributeError):
        pass
    for key, value in explicit.items():
        if value is not None:
            context[key] = value
    return context
