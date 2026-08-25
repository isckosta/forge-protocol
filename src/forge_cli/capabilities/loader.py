"""Deterministic loading of a Forge Capability definition (CAPABILITY.md).

locate -> read -> parse -> normalize -> return Capability model.

No package/fallback resolution, no discovery/enumeration, no registry, and
no execution: this module loads exactly one definition, given its path.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from forge_cli.capabilities.model import Capability

REQUIRED_SECTIONS: tuple[str, ...] = (
    "Identity",
    "Purpose",
    "Applicability",
    "Inputs",
    "Behavior",
    "Outputs",
    "Evidence Expectations",
)

_FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_SECTION_HEADING_PATTERN = re.compile(r"^##[ \t]+(.+?)[ \t]*$", re.MULTILINE)
_FENCE_PATTERN = re.compile(r"^(```|~~~)")


class CapabilityDefinitionError(ValueError):
    """Raised when a CAPABILITY.md definition cannot be loaded."""


def load_capability(path: Path) -> Capability:
    """Locate, read, parse, and normalize a CAPABILITY.md into a Capability."""
    if not path.is_file():
        raise CapabilityDefinitionError(f"Capability definition not found: {path}")

    text = path.read_text(encoding="utf-8")

    frontmatter_match = _FRONTMATTER_PATTERN.match(text)
    if frontmatter_match is None:
        raise CapabilityDefinitionError(
            f"Capability definition is missing its frontmatter block: {path}"
        )

    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    if not isinstance(frontmatter, dict):
        raise CapabilityDefinitionError(
            f"Capability definition frontmatter is not a mapping: {path}"
        )

    capability_id = frontmatter.get("capability")
    if not isinstance(capability_id, str) or not capability_id.strip():
        raise CapabilityDefinitionError(
            f"Capability definition is missing a non-empty 'capability' id: {path}"
        )

    schema = frontmatter.get("schema")
    if not isinstance(schema, int) or isinstance(schema, bool):
        raise CapabilityDefinitionError(
            f"Capability definition is missing an integer 'schema': {path}"
        )

    body = text[frontmatter_match.end() :]
    sections = _parse_sections(body, path)

    return Capability(
        id=capability_id.strip(),
        schema=schema,
        identity=sections["Identity"],
        purpose=sections["Purpose"],
        applicability=sections["Applicability"],
        inputs=sections["Inputs"],
        behavior=sections["Behavior"],
        outputs=sections["Outputs"],
        evidence_expectations=sections["Evidence Expectations"],
        source_path=path,
    )


def _parse_sections(body: str, path: Path) -> dict[str, str]:
    headings: list[tuple[str, int, int]] = []
    in_fence = False
    offset = 0
    for line in body.splitlines(keepends=True):
        if _FENCE_PATTERN.match(line):
            in_fence = not in_fence
        elif not in_fence:
            match = _SECTION_HEADING_PATTERN.match(line.rstrip("\n"))
            if match is not None:
                headings.append((match.group(1).strip(), offset, offset + len(line)))
        offset += len(line)

    sections: dict[str, str] = {}
    for index, (name, _, heading_end) in enumerate(headings):
        section_end = headings[index + 1][1] if index + 1 < len(headings) else len(body)
        sections[name] = body[heading_end:section_end].strip()

    for required in REQUIRED_SECTIONS:
        if not sections.get(required):
            raise CapabilityDefinitionError(
                f"Capability definition is missing required section '## {required}': {path}"
            )

    return sections
