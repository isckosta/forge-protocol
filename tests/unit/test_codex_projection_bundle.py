import importlib.util


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
    assert "full" in combined
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
