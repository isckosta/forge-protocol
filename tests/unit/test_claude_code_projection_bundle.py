import importlib.util

import pytest


def _projection_module():
    module_spec = importlib.util.find_spec("forge_cli.adapters.claude_code.projection")
    assert module_spec is not None, "Claude Code projection bundle is not implemented yet"
    from forge_cli.adapters.claude_code import projection

    return projection


def _canonical_input():
    projection = _projection_module()
    return projection.ClaudeCodeProjectionInput(
        flow_id="full",
        flow_content="stages:\n  - id: specification\n  - id: verification\n",
        contract_content="# Engineering Contract\nRepository-native Forge state is authoritative.\n",
    )


def test_projection_bundle_is_deterministic_for_identical_canonical_input() -> None:
    projection = _projection_module()
    canonical = _canonical_input()

    first = projection.generate_claude_code_projection_bundle(canonical)
    second = projection.generate_claude_code_projection_bundle(canonical)

    assert first == second
    assert tuple(resource.name for resource in first.resources) == tuple(
        sorted(resource.name for resource in first.resources)
    )


def test_projection_bundle_is_human_reviewable() -> None:
    projection = _projection_module()

    bundle = projection.generate_claude_code_projection_bundle(_canonical_input())

    assert bundle.adapter_id == "claude-code"
    assert bundle.flow_id == "full"
    assert bundle.resources
    for resource in bundle.resources:
        assert resource.content.strip()
        assert resource.digest

    combined = "\n".join(resource.content for resource in bundle.resources)
    assert "Forge" in combined
    assert "skills/forge/references/flows/full.yml" in {resource.name for resource in bundle.resources}
    assert "Repository-native Forge state is authoritative" in combined


def test_projection_bundle_has_no_implicit_publication_target() -> None:
    projection = _projection_module()

    bundle = projection.generate_claude_code_projection_bundle(_canonical_input())

    assert not hasattr(bundle, "publication_target")
    assert not hasattr(bundle, "target_path")
    assert all(not hasattr(resource, "target_path") for resource in bundle.resources)


def test_projection_resources_are_immutable() -> None:
    projection = _projection_module()

    bundle = projection.generate_claude_code_projection_bundle(_canonical_input())

    try:
        bundle.resources += ()
    except Exception as error:
        assert isinstance(error, (AttributeError, TypeError))
    else:
        raise AssertionError("Projection bundle must be immutable")


def test_projection_bundle_omits_artifact_structure_resource_when_not_provided() -> None:
    projection = _projection_module()

    bundle = projection.generate_claude_code_projection_bundle(_canonical_input())

    assert "skills/forge/references/artifact-structure.md" not in {
        resource.name for resource in bundle.resources
    }


def test_projection_bundle_includes_artifact_structure_when_provided() -> None:
    projection = _projection_module()

    bundle = projection.generate_claude_code_skill_bundle(
        contract_content="# Engineering Contract\nRepository-native Forge state is authoritative.\n",
        flows=(("full", "stages:\n  - id: specification\n  - id: verification\n"),),
        artifact_structure_content="# Canonical Artifact Structure\nProgressive Disclosure.\n",
    )

    by_name = {resource.name: resource for resource in bundle.resources}
    assert "skills/forge/references/artifact-structure.md" in by_name
    resource = by_name["skills/forge/references/artifact-structure.md"]
    assert "Progressive Disclosure" in resource.content
    assert resource.digest

    skill = by_name["skills/forge/SKILL.md"].content
    assert "Canonical Artifact Structure" not in skill
    assert "references/artifact-structure.md" in skill


def test_projection_bundle_renders_auto_interaction_language_by_default() -> None:
    projection = _projection_module()

    bundle = projection.generate_claude_code_projection_bundle(_canonical_input())

    skill = next(resource.content for resource in bundle.resources if resource.name == "skills/forge/SKILL.md")
    assert "Interaction language: auto" in skill


def test_projection_bundle_renders_explicit_interaction_language_when_provided() -> None:
    projection = _projection_module()

    bundle = projection.generate_claude_code_skill_bundle(
        contract_content="# Engineering Contract\nRepository-native Forge state is authoritative.\n",
        flows=(("full", "stages:\n  - id: specification\n  - id: verification\n"),),
        interaction_language="pt-BR",
    )

    skill = next(resource.content for resource in bundle.resources if resource.name == "skills/forge/SKILL.md")
    assert "Interaction language: pt-BR" in skill
    assert "C-072" in skill


def test_projection_bundle_rejects_conflicting_duplicate_effective_flow_ids() -> None:
    projection = _projection_module()

    with pytest.raises(ValueError) as error:
        projection.generate_claude_code_skill_bundle(
            contract_content="canonical contract",
            flows=(
                ("full", "flow: {id: full, name: first}"),
                ("full", "flow: {id: full, name: conflicting}"),
            ),
        )

    assert str(error.value) == "Duplicate effective Claude Code Flow: full"


# --- CHG-0018 FR-005/FR-006: the two mechanisms Codex has no equivalent of ---


def test_projection_bundle_includes_claude_md_pointer() -> None:
    """FR-005: a forge_owned CLAUDE.md pointer, distinct from SKILL.md,
    that references the Skill rather than restating its content (INV-001)."""
    projection = _projection_module()

    bundle = projection.generate_claude_code_projection_bundle(_canonical_input())

    by_name = {resource.name: resource for resource in bundle.resources}
    assert "CLAUDE.md" in by_name
    pointer = by_name["CLAUDE.md"].content
    assert "forge" in pointer.lower()
    assert ".claude/skills/forge/SKILL.md" in pointer
    # INV-001: does not restate the Contract's own normative text.
    assert "Repository-native Forge state is authoritative" not in pointer


def test_claude_md_pointer_carries_the_interaction_language_directive() -> None:
    projection = _projection_module()

    bundle = projection.generate_claude_code_skill_bundle(
        contract_content="contract",
        flows=(("full", "stages:\n  - id: verification\n"),),
        interaction_language="pt-BR",
    )
    pointer = next(resource.content for resource in bundle.resources if resource.name == "CLAUDE.md")
    assert "Interaction language: pt-BR" in pointer


def test_projection_bundle_includes_hook_script_and_frontmatter() -> None:
    """FR-006: an illustrative PreToolUse hook, scoped inside SKILL.md's
    own frontmatter (no separate settings.json merge -- DEC-002)."""
    projection = _projection_module()

    bundle = projection.generate_claude_code_projection_bundle(_canonical_input())

    by_name = {resource.name: resource for resource in bundle.resources}
    assert "skills/forge/hooks/check-manifest-edit.sh" in by_name
    hook = by_name["skills/forge/hooks/check-manifest-edit.sh"].content
    assert hook.startswith("#!/bin/sh")
    # Actual denial/allow behavior is verified end-to-end (real shell
    # execution) by test_hook_script_denies_in_place_mutation_of_review_control_paths,
    # not by string inspection here.

    skill = by_name["skills/forge/SKILL.md"].content
    front = skill.split("---", 2)[1]
    import yaml

    frontmatter = yaml.safe_load(front)
    assert frontmatter["hooks"]["PreToolUse"][0]["matcher"] == "Bash"
    assert frontmatter["hooks"]["PreToolUse"][0]["hooks"][0]["type"] == "command"
    assert "check-manifest-edit.sh" in frontmatter["hooks"]["PreToolUse"][0]["hooks"][0]["command"]


def test_hook_script_denies_in_place_mutation_of_review_control_paths() -> None:
    """Specification Review SR-001: the hook must deny in-place shell
    mutation of manifest.yml/provenance.yml/review.md but must not deny
    git add/commit/status/diff/show, cat, ls, or grep of the same paths."""
    import subprocess
    import json

    projection = _projection_module()
    bundle = projection.generate_claude_code_skill_bundle(
        contract_content="contract",
        flows=(("full", "stages:\n  - id: verification\n"),),
    )
    script = next(
        resource.content
        for resource in bundle.resources
        if resource.name == "skills/forge/hooks/check-manifest-edit.sh"
    )

    def run(command: str) -> tuple[int, str]:
        payload = json.dumps({"tool_input": {"command": command}})
        result = subprocess.run(
            ["sh", "-c", script],
            input=payload,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode, result.stdout

    denied = [
        "sed -i 's/current: in_progress/current: complete/' .forge/changes/CHG-0018-x/manifest.yml",
        "echo x > .forge/changes/CHG-0018-x/manifest.yml",
        "perl -i -pe 's/a/b/' .forge/changes/CHG-0018-x/provenance.yml",
        "truncate -s 0 .forge/changes/CHG-0018-x/review.md",
    ]
    for command in denied:
        code, stdout = run(command)
        assert code == 0
        assert '"permissionDecision":"deny"' in stdout, command

    allowed = [
        "git add .forge/changes/CHG-0018-x/manifest.yml",
        "git commit -m 'update manifest.yml'",
        "git status",
        "git diff .forge/changes/CHG-0018-x/manifest.yml",
        "cat .forge/changes/CHG-0018-x/manifest.yml",
        "ls .forge/changes/",
        "grep review .forge/changes/CHG-0018-x/manifest.yml",
        "ls -la",
    ]
    for command in allowed:
        code, stdout = run(command)
        assert code == 0
        assert stdout == "", command
