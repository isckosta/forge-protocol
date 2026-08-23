"""Failure-isolated bridge from accepted events to the existing FER writer."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import warnings

import yaml

from forge_cli.experience.capture import ExperienceCapturePolicy, ExperienceEvent
from forge_cli.experience.configuration import load_experience_configuration
from forge_cli.experience.configuration import ExperienceConfigurationError
from forge_cli.experience.model import ObservationInput
from forge_cli.experience.storage import ExperienceStorage, ExperienceStorageError


class ExperienceRecorder:
    def __init__(self, project_root: Path, *, context: dict[str, Any]) -> None:
        self.project_root = project_root
        self.context = dict(context)
        self.policy = ExperienceCapturePolicy()
        self.report_id: str | None = None
        self.last_diagnostic: str | None = None

    def capture(self, event: ExperienceEvent) -> Path | None:
        try:
            self.last_diagnostic = None
            if not load_experience_configuration(self.project_root).enabled:
                return None
            decision = self.policy.evaluate(event)
            if not decision.capture:
                return None
            existing = self._find_existing(decision.fingerprint)
            if existing is not None:
                self.report_id = existing.stem
                return existing
            storage = ExperienceStorage(
                self.project_root,
                context={**self.context, **event.context},
                report_id=self.report_id,
            )
            entry = ObservationInput(
                area=event.event_type,
                classification=decision.classification,
                expected=event.expected,
                observed=event.observed,
                evidence=event.evidence,
                impact="A Forge-owned invariant observation was captured automatically; cause remains uncertain.",
                capture={
                    "mode": decision.mode,
                    "detector": decision.detector,
                    "fingerprint": decision.fingerprint,
                },
            )
            path = storage.record(entry)
            self.report_id = path.stem
            return path
        except (OSError, yaml.YAMLError, ExperienceStorageError, ExperienceConfigurationError) as error:
            self.last_diagnostic = str(error)
            try:
                warnings.warn(
                    f"FER automatic capture failed without changing the primary operation: {error}",
                    RuntimeWarning,
                    stacklevel=2,
                )
            except Exception:
                pass
            return None

    def _find_existing(self, fingerprint: str) -> Path | None:
        reports_root = self.project_root / "dogfooding" / "reports"
        if not reports_root.is_dir() or reports_root.is_symlink():
            return None
        for path in sorted(reports_root.glob("FER-*.yml")):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError):
                continue
            observations = document.get("observations", []) if isinstance(document, dict) else []
            if any(
                isinstance(item, dict)
                and isinstance(item.get("capture"), dict)
                and item["capture"].get("fingerprint") == fingerprint
                for item in observations
            ):
                return path
        return None
