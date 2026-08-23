"""Deterministic human-readable projection of canonical FER reports."""

from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any


_GENERATED_NOTICE = "<!-- Generated from the canonical Forge Experience Report. Do not edit manually. -->"
_SOURCE_LABELS = {
    "forge_version": "Forge version",
    "protocol": "Protocol",
    "change": "Change",
    "flow": "Flow",
    "adapter": "Adapter",
    "harness": "Harness",
    "repository": "Repository",
    "commit": "Commit",
    "execution": "Execution",
    "context": "Context",
    "recorded_at": "Recorded at",
}
_SOURCE_ORDER = tuple(_SOURCE_LABELS)


def render_markdown(document: Mapping[str, Any]) -> str:
    """Render one validated canonical FER document without performing I/O."""
    report_id = _text(document.get("report"))
    sections = [_GENERATED_NOTICE, "", f"# {_escape(report_id)}"]

    source = document.get("source")
    if isinstance(source, Mapping) and source:
        sections.extend(["", "## Context"])
        for key in _ordered_source_keys(source):
            sections.append(f"- {_label(key)}: {_escape(_text(source[key]))}")
    if document.get("created_at") is not None:
        if not isinstance(source, Mapping) or not source:
            sections.extend(["", "## Context"])
        sections.append(f"- Created at: {_escape(_text(document['created_at']))}")

    observations = document.get("observations")
    positive_evidence = document.get("positive_evidence")
    follow_up_candidates = document.get("follow_up_candidates")
    observations = observations if isinstance(observations, list) else []
    positive_evidence = positive_evidence if isinstance(positive_evidence, list) else []
    follow_up_candidates = follow_up_candidates if isinstance(follow_up_candidates, list) else []

    if observations or positive_evidence:
        sections.extend(["", "## Summary"])
        sections.append(_summary(len(observations), len(positive_evidence)))

    if observations:
        sections.extend(["", "## Observations"])
        for observation in observations:
            sections.extend(_render_observation(observation))

    if positive_evidence:
        sections.extend(["", "## Positive Evidence"])
        for evidence in positive_evidence:
            if not isinstance(evidence, Mapping):
                continue
            evidence_id = _escape(_text(evidence.get("id")))
            area = _escape(_text(evidence.get("area")))
            sections.extend(
                [
                    "",
                    f"### {evidence_id} — {area}",
                    _escape(_text(evidence.get("observed"))),
                ]
            )

    if follow_up_candidates:
        sections.extend(["", "## Follow-up Candidates", ""])
        for candidate in follow_up_candidates:
            if not isinstance(candidate, Mapping):
                continue
            sections.append(
                "- "
                + _escape(_text(candidate.get("observation")))
                + " — "
                + _escape(_text(candidate.get("type")))
                + ": "
                + _escape(_text(candidate.get("summary")))
            )

    return "\n".join(sections).rstrip() + "\n"


def _render_observation(observation: Any) -> list[str]:
    if not isinstance(observation, Mapping):
        return []
    rendered = [
        "",
        f"### {_escape(_text(observation.get('id')))} — {_escape(_text(observation.get('area')))}",
        "**Classification**",
        _classification(observation.get("classification")),
        "",
        "**Expected**",
        _escape(_text(observation.get("expected"))),
        "",
        "**Observed**",
        _escape(_text(observation.get("observed"))),
        "",
        "**Impact**",
        _escape(_text(observation.get("impact"))),
        "",
        "**Evidence**",
    ]
    evidence = observation.get("evidence")
    if isinstance(evidence, list):
        rendered.extend(f"- {_escape(_text(item))}" for item in evidence)
    for field, label in (("workaround", "Workaround"), ("follow_up", "Possible follow-up")):
        value = observation.get(field)
        if value is not None and _text(value).strip():
            rendered.extend(["", f"**{label}**", _escape(_text(value))])
    capture = observation.get("capture")
    if isinstance(capture, Mapping):
        rendered.extend(
            [
                "",
                "**Capture**",
                "Mode: " + _escape(_text(capture.get("mode"))),
                "Detector: " + _escape(_text(capture.get("detector"))),
            ]
        )
    return rendered


def _ordered_source_keys(source: Mapping[str, Any]) -> list[str]:
    known = [key for key in _SOURCE_ORDER if key in source]
    unknown = sorted((str(key) for key in source if key not in _SOURCE_LABELS), key=str)
    return known + unknown


def _label(key: str) -> str:
    return _SOURCE_LABELS.get(key, key.replace("_", " ").capitalize())


def _classification(value: Any) -> str:
    return {
        "forge_problem": "Forge problem",
        "project_problem": "Project problem",
        "uncertain": "Uncertain",
    }.get(_text(value), _escape(_text(value)))


def _summary(observation_count: int, positive_count: int) -> str:
    observations = f"{observation_count} observation" + ("s" if observation_count != 1 else "")
    evidence = f"{positive_count} positive evidence entr" + ("ies" if positive_count != 1 else "y")
    return f"{observations} and {evidence} were recorded."


def _text(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str) and hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _escape(value: str) -> str:
    escaped_lines = []
    for line in value.replace("\\", "\\\\").split("\n"):
        for character in "`*_[]()#!|<>":
            line = line.replace(character, "\\" + character)
        marker = re.match(r"^(\s*)(?:[-+*>]|\d+[.)](?:\s|$))", line)
        if marker:
            line = marker.group(1) + "\\" + line[len(marker.group(1)) :]
        escaped_lines.append(line)
    return "  \n".join(escaped_lines)
