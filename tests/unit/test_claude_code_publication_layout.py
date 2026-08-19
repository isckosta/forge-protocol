from __future__ import annotations

try:
    from forge_cli.adapters.claude_code.targets import resolve_publication_target, resolve_resource_path
except ImportError:
    resolve_publication_target = None
    resolve_resource_path = None


def _require_behavior() -> None:
    assert resolve_publication_target is not None
    assert resolve_resource_path is not None, "Claude Code publication resource layout is not implemented yet"


def test_target_is_a_root_for_multiple_resources() -> None:
    _require_behavior()
    target = resolve_publication_target(explicit_target="tools/claude-code")
    assert target is not None
    assert target.root == "tools/claude-code"
    assert resolve_resource_path(target, "forge-flow.md") == "tools/claude-code/forge-flow.md"
    assert resolve_resource_path(target, "forge-contract.md") == "tools/claude-code/forge-contract.md"


def test_resource_name_must_stay_within_publication_root() -> None:
    _require_behavior()
    target = resolve_publication_target(explicit_target="tools/claude-code")
    assert target is not None

    assert resolve_resource_path(target, "nested/item.md") == "tools/claude-code/nested/item.md"

    for name in ("../item.md", "/item.md", r"a\b.md", "a/../b.md"):
        try:
            resolve_resource_path(target, name)
        except ValueError:
            continue
        raise AssertionError(name)


def test_default_target_is_the_shared_claude_code_configuration_root() -> None:
    """CHG-0018 architecture.md DEC-001 Correction: the Skill subtree and
    the CLAUDE.md pointer must share one ownership-root ceiling
    (ownership.require_publication_root_ownership requires every artifact
    to be a strict descendant of one root), so the default target is
    `.claude`, not `.claude/skills/forge`."""
    from forge_cli.adapters.claude_code.driver import ClaudeCodeDriver

    assert ClaudeCodeDriver().default_target == ".claude"
