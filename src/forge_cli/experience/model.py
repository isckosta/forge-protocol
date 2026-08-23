"""FER input model and validation."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Literal


Classification = Literal["forge_problem", "project_problem", "uncertain"]
_MAX_TEXT_LENGTH = 2000
_SENSITIVE_TEXT = re.compile(
    r"(?i)(bearer\s+[A-Za-z0-9._~+/=-]+|(?:api[_-]?key|token|password|secret)\s*[:=])"
)


class ExperienceInputError(ValueError):
    """Raised when contributor-provided FER input is incomplete or unsafe."""


@dataclass(frozen=True)
class ObservationInput:
    area: str
    classification: Classification
    expected: str
    observed: str
    evidence: tuple[str, ...]
    impact: str
    workaround: str | None = None
    follow_up: str | None = None
    capture: dict[str, str] | None = None


@dataclass(frozen=True)
class PositiveEvidenceInput:
    area: str
    observed: str


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExperienceInputError(f"{field} must be a non-empty string.")
    return ensure_safe_text(value.strip(), field)


def ensure_safe_text(value: str, field: str) -> str:
    if len(value) > _MAX_TEXT_LENGTH:
        raise ExperienceInputError(f"{field} must remain concise and be at most {_MAX_TEXT_LENGTH} characters.")
    if _SENSITIVE_TEXT.search(value):
        raise ExperienceInputError(f"{field} contains sensitive material and cannot be recorded.")
    return value


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _text(value, field)


def parse_record_input(document: Any) -> ObservationInput | PositiveEvidenceInput:
    if not isinstance(document, dict):
        raise ExperienceInputError("FER input must be a mapping.")
    if (observation := document.get("observation")) is not None:
        if not isinstance(observation, dict):
            raise ExperienceInputError("observation must be a mapping.")
        classification = observation.get("classification")
        if classification not in {"forge_problem", "project_problem", "uncertain"}:
            raise ExperienceInputError("classification is invalid.")
        evidence = observation.get("evidence")
        if not isinstance(evidence, list) or not evidence or not all(isinstance(item, str) and item.strip() for item in evidence):
            raise ExperienceInputError("evidence must be a non-empty list of strings.")
        return ObservationInput(
            area=_text(observation.get("area"), "area"),
            classification=classification,
            expected=_text(observation.get("expected"), "expected"),
            observed=_text(observation.get("observed"), "observed"),
            evidence=tuple(ensure_safe_text(item.strip(), "evidence") for item in evidence),
            impact=_text(observation.get("impact"), "impact"),
            workaround=_optional_text(observation.get("workaround"), "workaround"),
            follow_up=_optional_text(observation.get("follow_up"), "follow_up"),
        )
    positive = document.get("positive_evidence")
    if isinstance(positive, dict):
        return PositiveEvidenceInput(
            area=_text(positive.get("area"), "area"),
            observed=_text(positive.get("observed"), "observed"),
        )
    raise ExperienceInputError("Input must contain observation or positive_evidence.")
