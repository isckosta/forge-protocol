"""Structured Forge experience events and the conservative capture policy."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Literal

from forge_cli.experience.model import Classification, ExperienceInputError, ensure_safe_text


CaptureMode = Literal["automatic"]


@dataclass(frozen=True)
class ExperienceEvent:
    event_type: str
    detector: str
    expected: str
    observed: str
    evidence: tuple[str, ...]
    context: dict[str, str]

    def __post_init__(self) -> None:
        if self.event_type != "adapter_conformance":
            return
        ensure_safe_text(self.detector, "detector")
        ensure_safe_text(self.expected, "expected")
        ensure_safe_text(self.observed, "observed")
        if not self.evidence:
            raise ExperienceInputError("event evidence must not be empty.")
        for item in self.evidence:
            ensure_safe_text(item, "evidence")
        for key, value in self.context.items():
            ensure_safe_text(str(key), "context key")
            ensure_safe_text(str(value), "context value")


@dataclass(frozen=True)
class CaptureDecision:
    capture: bool
    classification: Classification = "uncertain"
    fingerprint: str = ""
    mode: CaptureMode = "automatic"
    detector: str = ""


class ExperienceCapturePolicy:
    """Allow only explicitly supported, Forge-owned material event types."""

    _SUPPORTED = frozenset({"adapter_conformance"})
    _VOLATILE_CONTEXT = frozenset({"recorded_at", "timestamp", "commit"})

    def evaluate(self, event: ExperienceEvent) -> CaptureDecision:
        if event.event_type not in self._SUPPORTED:
            return CaptureDecision(capture=False)
        stable_context = {
            str(key): str(value)
            for key, value in event.context.items()
            if key not in self._VOLATILE_CONTEXT
        }
        identity = {
            "event_type": event.event_type,
            "change": stable_context.get("change", ""),
            "execution": stable_context.get("execution", ""),
            "boundary": stable_context.get("boundary", ""),
            "expected": event.expected.strip(),
            "observed": event.observed.strip(),
        }
        encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return CaptureDecision(
            capture=True,
            classification="uncertain",
            fingerprint=hashlib.sha256(encoded).hexdigest(),
            detector=event.detector,
        )


def event_from_conformance(finding: Any, *, context: dict[str, str]) -> ExperienceEvent:
    """Convert one structured Adapter finding into a bounded FER event."""
    subject = getattr(finding, "subject", "")
    code = str(getattr(finding, "code", "adapter-conformance"))
    observed = f"{code}{': ' + subject if subject else ''}"
    return ExperienceEvent(
        event_type="adapter_conformance",
        detector="adapter-conformance",
        expected="The Adapter representation preserves the required Forge semantics.",
        observed=observed,
        evidence=(observed,),
        context={**context, "boundary": "adapter-conformance"},
    )
