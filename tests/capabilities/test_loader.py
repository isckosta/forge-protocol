from pathlib import Path

import pytest

from forge_cli.capabilities.loader import CapabilityDefinitionError, load_capability

_ALL_SECTIONS = (
    "Identity",
    "Purpose",
    "Applicability",
    "Inputs",
    "Behavior",
    "Outputs",
    "Evidence Expectations",
)


def _well_formed_text(*, pad_sections: bool = False) -> str:
    pad = "  \n\n" if pad_sections else ""
    body = "\n".join(f"## {name}\n{pad}{name} body text.{pad}\n" for name in _ALL_SECTIONS)
    return f"---\ncapability: sample\nschema: 1\n---\n\n# Capability - Sample\n\n{body}"


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "CAPABILITY.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_loads_well_formed_definition_into_normalized_model(tmp_path: Path) -> None:
    path = _write(tmp_path, _well_formed_text(pad_sections=True))

    capability = load_capability(path)

    assert capability.id == "sample"
    assert capability.schema == 1
    assert capability.source_path == path
    assert capability.identity == "Identity body text."
    assert capability.purpose == "Purpose body text."
    assert capability.applicability == "Applicability body text."
    assert capability.inputs == "Inputs body text."
    assert capability.behavior == "Behavior body text."
    assert capability.outputs == "Outputs body text."
    assert capability.evidence_expectations == "Evidence Expectations body text."


def test_loading_the_same_unchanged_file_twice_is_deterministic(tmp_path: Path) -> None:
    path = _write(tmp_path, _well_formed_text())

    first = load_capability(path)
    second = load_capability(path)

    assert first == second


def test_missing_file_raises_capability_definition_error(tmp_path: Path) -> None:
    missing = tmp_path / "CAPABILITY.md"

    with pytest.raises(CapabilityDefinitionError, match=str(missing)):
        load_capability(missing)


def test_missing_frontmatter_raises_capability_definition_error(tmp_path: Path) -> None:
    path = _write(tmp_path, "# Capability - Sample\n\nNo frontmatter here.\n")

    with pytest.raises(CapabilityDefinitionError, match="frontmatter"):
        load_capability(path)


@pytest.mark.parametrize(
    "frontmatter",
    [
        "---\nschema: 1\n---\n",
        "---\ncapability: ''\nschema: 1\n---\n",
        "---\ncapability: sample\n---\n",
        "---\ncapability: sample\nschema: not-an-int\n---\n",
    ],
)
def test_invalid_frontmatter_identity_raises_capability_definition_error(
    tmp_path: Path, frontmatter: str
) -> None:
    body = "\n".join(f"## {name}\n{name} body text.\n" for name in _ALL_SECTIONS)
    path = _write(tmp_path, f"{frontmatter}\n{body}")

    with pytest.raises(CapabilityDefinitionError):
        load_capability(path)


@pytest.mark.parametrize("missing_section", _ALL_SECTIONS)
def test_missing_required_section_raises_capability_definition_error(
    tmp_path: Path, missing_section: str
) -> None:
    remaining = [name for name in _ALL_SECTIONS if name != missing_section]
    body = "\n".join(f"## {name}\n{name} body text.\n" for name in remaining)
    path = _write(tmp_path, f"---\ncapability: sample\nschema: 1\n---\n\n{body}")

    with pytest.raises(CapabilityDefinitionError, match=missing_section):
        load_capability(path)


@pytest.mark.parametrize("empty_section", _ALL_SECTIONS)
def test_empty_required_section_raises_capability_definition_error(
    tmp_path: Path, empty_section: str
) -> None:
    body = "\n".join(
        f"## {name}\n{'   ' if name == empty_section else name + ' body text.'}\n"
        for name in _ALL_SECTIONS
    )
    path = _write(tmp_path, f"---\ncapability: sample\nschema: 1\n---\n\n{body}")

    with pytest.raises(CapabilityDefinitionError, match=empty_section):
        load_capability(path)


def test_heading_shaped_line_inside_a_fenced_code_block_is_not_a_new_section(
    tmp_path: Path,
) -> None:
    sections = {name: f"{name} body text." for name in _ALL_SECTIONS}
    sections["Behavior"] = (
        "Behavior text before the example.\n"
        "```\n"
        "## Fake Heading Inside Code Block\n"
        "```\n"
        "Behavior text after the example."
    )
    body = "\n".join(f"## {name}\n{text}\n" for name, text in sections.items())
    path = _write(tmp_path, f"---\ncapability: sample\nschema: 1\n---\n\n{body}")

    capability = load_capability(path)

    assert capability.behavior == sections["Behavior"]
    assert "Fake Heading" not in capability.outputs
