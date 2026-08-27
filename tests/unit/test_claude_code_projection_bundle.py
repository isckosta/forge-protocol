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


def test_projection_bundle_omits_decision_rules_resource_when_not_provided() -> None:
    """CHG-0021 FR-005/AC-005: backward compatibility, mirroring
    artifact_structure_content's own CHG-0016 guard above."""
    projection = _projection_module()

    bundle = projection.generate_claude_code_projection_bundle(_canonical_input())

    assert "skills/forge/references/decision-rules.md" not in {
        resource.name for resource in bundle.resources
    }
    assert "references/decision-rules.md" not in {r.name for r in bundle.resources}


def test_projection_bundle_includes_decision_rules_when_provided() -> None:
    """CHG-0021 FR-002/AC-002."""
    projection = _projection_module()

    bundle = projection.generate_claude_code_skill_bundle(
        contract_content="# Engineering Contract\nRepository-native Forge state is authoritative.\n",
        flows=(("full", "stages:\n  - id: specification\n  - id: verification\n"),),
        decision_rules_content="# Forge Decision Structural Rules\nclass: product, contract.\n",
    )

    by_name = {resource.name: resource for resource in bundle.resources}
    assert "skills/forge/references/decision-rules.md" in by_name
    resource = by_name["skills/forge/references/decision-rules.md"]
    assert "class: product, contract." in resource.content
    assert resource.digest

    skill = by_name["skills/forge/SKILL.md"].content
    assert "class: product, contract." not in skill
    assert "references/decision-rules.md" in skill


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


def test_only_the_hook_resource_is_marked_executable() -> None:
    """CHG-0049 FR-002: the Adapter projection is the source of truth for
    which generated paths must be executable -- exactly the hook, nothing
    else."""
    projection = _projection_module()

    bundle = projection.generate_claude_code_projection_bundle(_canonical_input())

    executable = {
        resource.name for resource in bundle.resources if resource.executable
    }
    assert executable == {"skills/forge/hooks/check-manifest-edit.sh"}


def test_projection_bundle_hook_frontmatter_also_matches_edit_and_write() -> None:
    """CHG-0045 FR-006/TDD-009: the same guard must not be trivially
    bypassed by switching tools -- Edit/Write must be matched alongside
    Bash, pointed at the same generated script."""
    projection = _projection_module()
    bundle = projection.generate_claude_code_projection_bundle(_canonical_input())
    by_name = {resource.name: resource for resource in bundle.resources}
    skill = by_name["skills/forge/SKILL.md"].content
    import yaml

    frontmatter = yaml.safe_load(skill.split("---", 2)[1])
    matchers = {entry["matcher"] for entry in frontmatter["hooks"]["PreToolUse"]}
    assert matchers == {"Bash", "Edit", "Write"}
    for entry in frontmatter["hooks"]["PreToolUse"]:
        assert "check-manifest-edit.sh" in entry["hooks"][0]["command"]


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
        # R001 regression guard: a genuine mutation must still be caught
        # even with an unrelated command chained before or after it.
        "sed -i 's/a/b/' .forge/changes/CHG-0018-x/manifest.yml && echo done",
        "echo start; sed -i 's/a/b/' .forge/changes/CHG-0018-x/manifest.yml",
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
        # Strict Review R001 (CHG-0018 Iteration 1): a naive whole-string
        # match previously denied these two, even though both are, in
        # substance, an ordinary git add/commit of a protected path with
        # an unrelated '>' elsewhere in the same command line.
        "git status > /tmp/status.txt && git add .forge/changes/CHG-0018-x/manifest.yml",
        'git commit -m "docs(chg-0018): note -- see .forge/changes/CHG-0018-x/manifest.yml > also check review.md"',
    ]
    for command in allowed:
        code, stdout = run(command)
        assert code == 0
        assert stdout == "", command


def test_generated_skill_does_not_grow_relative_to_the_pre_chg_0045_baseline() -> None:
    """CHG-0045 NFR-003/TDD-014: removing the per-Flow-duplicated
    independence block and stale Plan-Decision sentence must not be offset
    by new bulk. Baseline (180 lines) captured from `main` (pre-CHG-0045)
    for this exact three-Flow, Protocol-2 fixture before this Change's
    projection.py edits landed."""
    projection = _projection_module()
    flow = (
        "gates:\n  before_implementation:\n    require: [plan_complete]\n"
        "  before_completion:\n    require: [verification_passed, review_passed]\n"
    )
    bundle = projection.generate_claude_code_skill_bundle(
        contract_content="contract",
        flows=(("fast", flow), ("standard", flow), ("full", flow)),
        protocol_id=2,
    )
    skill = next(resource.content for resource in bundle.resources if resource.name == "skills/forge/SKILL.md")
    PRE_CHG_0045_BASELINE_LINE_COUNT = 180
    assert len(skill.splitlines()) <= PRE_CHG_0045_BASELINE_LINE_COUNT


def test_hook_script_denies_edit_and_write_mutation_of_review_control_paths() -> None:
    """CHG-0045 FR-006/TDD-010/TDD-011: the same three protected paths must
    be denied when mutated through Edit/Write, and unrelated Edit/Write
    calls must still be allowed (no false positive)."""
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

    def run(tool_name: str, file_path: str) -> tuple[int, str]:
        payload = json.dumps({"tool_name": tool_name, "tool_input": {"file_path": file_path}})
        result = subprocess.run(
            ["sh", "-c", script],
            input=payload,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode, result.stdout

    for tool_name in ("Edit", "Write"):
        for path in (
            ".forge/changes/CHG-0018-x/manifest.yml",
            ".forge/changes/CHG-0018-x/provenance.yml",
            ".forge/changes/CHG-0018-x/review.md",
        ):
            code, stdout = run(tool_name, path)
            assert code == 0
            assert '"permissionDecision":"deny"' in stdout, (tool_name, path)

        code, stdout = run(tool_name, "src/forge_cli/adapters/claude_code/projection.py")
        assert code == 0
        assert stdout == "", tool_name
