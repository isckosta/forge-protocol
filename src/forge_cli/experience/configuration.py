"""Repository-local FER enablement configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ExperienceConfigurationError(RuntimeError):
    """Raised when explicitly requested FER configuration is invalid."""


@dataclass(frozen=True)
class ExperienceReportingConfiguration:
    enabled: bool


def load_experience_configuration(project_root: Path) -> ExperienceReportingConfiguration:
    path = project_root / ".forge" / "contributor.yml"
    if not path.exists():
        return ExperienceReportingConfiguration(enabled=False)
    try:
        document: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ExperienceConfigurationError(str(error)) from error
    if not isinstance(document, dict) or document.get("schema") != "forge/contributor@1":
        raise ExperienceConfigurationError("Invalid contributor configuration schema.")
    reporting = document.get("experience_reporting")
    if not isinstance(reporting, dict) or not isinstance(reporting.get("enabled"), bool):
        raise ExperienceConfigurationError("experience_reporting.enabled must be a boolean.")
    return ExperienceReportingConfiguration(enabled=reporting["enabled"])


def write_experience_configuration(project_root: Path, enabled: bool) -> Path:
    forge_root = project_root / ".forge"
    forge_root.mkdir(parents=True, exist_ok=True)
    path = forge_root / "contributor.yml"
    path.write_text(
        yaml.safe_dump(
            {
                "schema": "forge/contributor@1",
                "experience_reporting": {"enabled": enabled},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path
