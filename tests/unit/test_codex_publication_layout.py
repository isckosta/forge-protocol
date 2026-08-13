from __future__ import annotations

try:
    from forge_cli.adapters.codex.targets import resolve_publication_target, resolve_resource_path
except ImportError:
    resolve_publication_target = None
    resolve_resource_path = None


def _require_behavior() -> None:
    assert resolve_publication_target is not None
    assert resolve_resource_path is not None, "Codex publication resource layout is not implemented yet"


def test_target_is_a_root_for_multiple_resources() -> None:
    _require_behavior()
    target = resolve_publication_target(explicit_target="tools/codex")
    assert target is not None
    assert target.root == "tools/codex"
    assert resolve_resource_path(target, "forge-flow.md") == "tools/codex/forge-flow.md"
    assert resolve_resource_path(target, "forge-contract.md") == "tools/codex/forge-contract.md"


def test_resource_name_must_stay_within_publication_root() -> None:
    _require_behavior()
    target = resolve_publication_target(explicit_target="tools/codex")
    assert target is not None

    assert resolve_resource_path(target, "nested/item.md") == "tools/codex/nested/item.md"

    for name in ("../item.md", "/item.md", r"a\b.md", "a/../b.md"):
        try:
            resolve_resource_path(target, name)
        except ValueError:
            continue
        raise AssertionError(name)
