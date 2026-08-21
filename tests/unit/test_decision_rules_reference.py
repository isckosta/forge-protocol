"""CHG-0021: Decision structural rules rendered from the live validation
constants -- never a hand-duplicated copy (NFR-001). TDD-001 asserts the
renderer against the real imported constants, not a re-typed literal, so
this test fails if a constant changes and the renderer does not follow.
TDD-006 asserts both Adapters project byte-identical content for the same
resolved value.
"""
from __future__ import annotations

import re

from forge_cli.validation import (
    _DEC_AUTHORITIES,
    _DEC_AUTHORITY_FLOOR,
    _DEC_CLASSES,
    _DEC_MATERIALITY,
    _DEC_OWNING_BY_CLASS,
    _DEC_RESOLVED_VIA,
    _DEC_STATUSES,
    render_decision_rules_reference,
)


def _lines(rendered: str) -> list[str]:
    return rendered.splitlines()


def test_render_decision_rules_reference_contains_every_enum_value() -> None:
    rendered = render_decision_rules_reference()

    for value in (*_DEC_CLASSES, *_DEC_MATERIALITY, *_DEC_STATUSES, *_DEC_AUTHORITIES, *_DEC_RESOLVED_VIA):
        assert re.search(rf"\b{re.escape(value)}\b", rendered), f"{value!r} missing from rendered reference"


def test_render_decision_rules_reference_pairs_class_with_its_valid_owning_artifacts() -> None:
    rendered = render_decision_rules_reference()
    lines = _lines(rendered)

    for cls, owning in _DEC_OWNING_BY_CLASS.items():
        matching = [line for line in lines if re.search(rf"`{re.escape(cls)}`", line)]
        assert matching, f"no rendered line names class {cls!r}"
        for artifact in owning:
            assert any(artifact in line for line in matching), (
                f"class {cls!r} line does not name owning_artifact {artifact!r}: {matching}"
            )


def test_render_decision_rules_reference_states_authority_floor_per_class() -> None:
    rendered = render_decision_rules_reference()
    lines = _lines(rendered)

    for cls, floor in _DEC_AUTHORITY_FLOOR.items():
        matching = [line for line in lines if re.search(rf"`{re.escape(cls)}`", line) and floor in line]
        assert matching, f"no rendered line pairs class {cls!r} with authority floor {floor!r}"


def test_render_decision_rules_reference_discloses_its_own_generation() -> None:
    rendered = render_decision_rules_reference()

    assert "forge validate" in rendered
    assert "generated" in rendered.lower()


def test_render_decision_rules_reference_is_deterministic() -> None:
    assert render_decision_rules_reference() == render_decision_rules_reference()


def test_decision_rules_reference_is_byte_identical_across_both_adapters() -> None:
    """TDD-006 / AC-006: one resolved value threaded through both bundle
    generators must not diverge -- not merely that each generator echoes
    whatever it individually receives (already covered per-Adapter)."""
    from forge_cli.adapters.claude_code import projection as claude_code_projection
    from forge_cli.adapters.codex import projection as codex_projection

    resolved = render_decision_rules_reference()

    claude_bundle = claude_code_projection.generate_claude_code_skill_bundle(
        contract_content="# Engineering Contract\nRepository-native Forge state is authoritative.\n",
        flows=(("full", "stages:\n  - id: specification\n  - id: verification\n"),),
        decision_rules_content=resolved,
    )
    codex_bundle = codex_projection.generate_codex_skill_bundle(
        contract_content="# Engineering Contract\nRepository-native Forge state is authoritative.\n",
        flows=(("full", "stages:\n  - id: specification\n  - id: verification\n"),),
        decision_rules_content=resolved,
    )

    claude_resource = next(
        r for r in claude_bundle.resources if r.name == "skills/forge/references/decision-rules.md"
    )
    codex_resource = next(r for r in codex_bundle.resources if r.name == "references/decision-rules.md")

    assert claude_resource.content == codex_resource.content == resolved.rstrip() + "\n"
