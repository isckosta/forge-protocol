import importlib.util

import pytest


def _projection_module():
    module_spec = importlib.util.find_spec("forge_cli.adapters.codex.projection")
    assert module_spec is not None, "Codex projection bundle is not implemented yet"
    from forge_cli.adapters.codex import projection

    return projection


def _canonical_input():
    projection = _projection_module()
    return projection.CodexProjectionInput(
        flow_id="full",
        flow_content="stages:\n  - id: specification\n  - id: verification\n",
        contract_content="# Engineering Contract\nRepository-native Forge state is authoritative.\n",
    )


def test_projection_bundle_is_deterministic_for_identical_canonical_input() -> None:
    projection = _projection_module()
    canonical = _canonical_input()

    first = projection.generate_codex_projection_bundle(canonical)
    second = projection.generate_codex_projection_bundle(canonical)

    assert first == second
    assert tuple(resource.name for resource in first.resources) == tuple(
        sorted(resource.name for resource in first.resources)
    )


def test_projection_bundle_is_human_reviewable() -> None:
    projection = _projection_module()

    bundle = projection.generate_codex_projection_bundle(_canonical_input())

    assert bundle.adapter_id == "codex"
    assert bundle.flow_id == "full"
    assert bundle.resources
    for resource in bundle.resources:
        assert resource.content.strip()
        assert resource.digest

    combined = "\n".join(resource.content for resource in bundle.resources)
    assert "Forge" in combined
    assert "references/flows/full.yml" in {resource.name for resource in bundle.resources}
    assert "Repository-native Forge state is authoritative" in combined


def test_projection_bundle_has_no_implicit_publication_target() -> None:
    projection = _projection_module()

    bundle = projection.generate_codex_projection_bundle(_canonical_input())

    assert not hasattr(bundle, "publication_target")
    assert not hasattr(bundle, "target_path")
    assert all(not hasattr(resource, "target_path") for resource in bundle.resources)


def test_projection_resources_are_immutable() -> None:
    projection = _projection_module()

    bundle = projection.generate_codex_projection_bundle(_canonical_input())

    try:
        bundle.resources += ()
    except Exception as error:
        assert isinstance(error, (AttributeError, TypeError))
    else:
        raise AssertionError("Projection bundle must be immutable")


def test_projection_bundle_omits_artifact_structure_resource_when_not_provided() -> None:
    """Backward compatibility: existing callers that never pass the new field
    must keep getting exactly the same resource set as before CHG-0016."""
    projection = _projection_module()

    bundle = projection.generate_codex_projection_bundle(_canonical_input())

    assert "references/artifact-structure.md" not in {
        resource.name for resource in bundle.resources
    }


def test_projection_bundle_includes_artifact_structure_when_provided() -> None:
    """CHG-0016 FR-009/AC-009: the canonical guidance is projected by
    reference, the same way Contract and Flow content already are."""
    projection = _projection_module()

    bundle = projection.generate_codex_skill_bundle(
        contract_content="# Engineering Contract\nRepository-native Forge state is authoritative.\n",
        flows=(("full", "stages:\n  - id: specification\n  - id: verification\n"),),
        artifact_structure_content="# Canonical Artifact Structure\nProgressive Disclosure.\n",
    )

    by_name = {resource.name: resource for resource in bundle.resources}
    assert "references/artifact-structure.md" in by_name
    resource = by_name["references/artifact-structure.md"]
    assert "Progressive Disclosure" in resource.content
    assert resource.digest

    skill = by_name["SKILL.md"].content
    assert "Canonical Artifact Structure" not in skill
    assert "references/artifact-structure.md" in skill


def test_projection_bundle_renders_auto_interaction_language_by_default() -> None:
    """CHG-0017 FR-004/AC-006: no `interaction_language` passed -> the
    auto/fallback instruction line, citing C-070-C-073."""
    projection = _projection_module()

    bundle = projection.generate_codex_projection_bundle(_canonical_input())

    skill = next(resource.content for resource in bundle.resources if resource.name == "SKILL.md")
    assert "Interaction language: auto" in skill
    assert "C-070" in skill and "C-073" in skill


def test_projection_bundle_renders_explicit_interaction_language_when_provided() -> None:
    """CHG-0017 FR-004/AC-005: an explicit `interaction_language` renders
    the deterministic-precedence instruction line, citing C-072."""
    projection = _projection_module()

    bundle = projection.generate_codex_skill_bundle(
        contract_content="# Engineering Contract\nRepository-native Forge state is authoritative.\n",
        flows=(("full", "stages:\n  - id: specification\n  - id: verification\n"),),
        interaction_language="pt-BR",
    )

    skill = next(resource.content for resource in bundle.resources if resource.name == "SKILL.md")
    assert "Interaction language: pt-BR" in skill
    assert "C-072" in skill
    assert "auto" not in skill.split("Interaction language:", 1)[1].split("\n", 1)[0]


def test_projection_bundle_rejects_conflicting_duplicate_effective_flow_ids() -> None:
    """Duplicate IDs must fail before the public renderer can emit any links."""
    projection = _projection_module()

    with pytest.raises(ValueError) as error:
        projection.generate_codex_skill_bundle(
            contract_content="canonical contract",
            flows=(
                ("full", "flow: {id: full, name: first}"),
                ("full", "flow: {id: full, name: conflicting}"),
            ),
        )

    assert str(error.value) == "Duplicate effective Codex Flow: full"
