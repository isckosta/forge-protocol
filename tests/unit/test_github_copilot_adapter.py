from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from forge_cli.adapters.driver import AdapterProjectionContext
from forge_cli.adapters.github_copilot.descriptor import load_github_copilot_adapter_descriptor
from forge_cli.adapters.github_copilot.driver import GitHubCopilotDriver
from forge_cli.adapters.github_copilot.targets import validate_publication_root
from forge_cli.adapters.packaged import build_packaged_registry


def _context() -> AdapterProjectionContext:
    return AdapterProjectionContext(
        project_protocol=2,
        flows=(("standard", "flow: standard\nstages: []\ngates: {}\n"),),
        contract_content="contract",
        target=".github",
        artifact_structure_content="artifacts",
        decision_rules_content="decisions",
    )


def test_github_copilot_is_packaged_and_has_official_evidence() -> None:
    descriptor = load_github_copilot_adapter_descriptor()

    assert descriptor.manifest.adapter_id == "github-copilot"
    assert descriptor.manifest.harness == "github-copilot"
    assert {item.capability for item in descriptor.evidence} == {
        "persistent_instructions",
        "skills",
        "hooks",
        "generated_files",
        "agent_roles",
        "commands",
    }
    assert any("github.com" in item.source for item in descriptor.evidence)


def test_github_copilot_projection_is_deterministic_and_uses_native_paths() -> None:
    driver = GitHubCopilotDriver()

    first = driver.project(_context())
    second = driver.project(_context())

    assert first == second
    paths = [artifact.path for artifact in first.artifacts]
    assert ".github/copilot-instructions.md" in paths
    assert ".github/skills/forge/SKILL.md" in paths
    assert ".github/skills/forge/references/engineering-contract.md" in paths
    assert ".github/hooks/forge-review-control.json" in paths
    assert all(path.startswith(".github/") for path in paths)

    pointer = next(
        artifact.content
        for artifact in first.artifacts
        if artifact.path.endswith("copilot-instructions.md")
    )
    assert "does not restate" in pointer
    assert "Engineering Contract" not in pointer


def test_github_copilot_hook_denies_review_control_metadata() -> None:
    projection = GitHubCopilotDriver().project(_context())
    hook = next(
        artifact.content
        for artifact in projection.artifacts
        if artifact.path.endswith("forge-review-control.json")
    )
    data = json.loads(hook)

    assert data["version"] == 1
    assert data["hooks"]["preToolUse"][0]["type"] == "command"
    script = next(
        artifact.content
        for artifact in projection.artifacts
        if artifact.path.endswith("forge-review-control.sh")
    )
    assert "manifest\\.yml" in script
    assert "provenance\\.yml" in script
    assert "review\\.md" in script


def test_github_copilot_hook_allows_read_only_commands() -> None:
    projection = GitHubCopilotDriver().project(_context())
    script = next(
        artifact.content
        for artifact in projection.artifacts
        if artifact.path.endswith("forge-review-control.sh")
    )
    script_path = Path(__file__).with_name("forge-review-control.sh")
    script_path.write_text(script, encoding="utf-8")
    try:
        result = subprocess.run(
            ["/bin/sh", str(script_path)],
            input=json.dumps({
                "toolName": "bash",
                "toolArgs": {"command": "git status -- .forge/changes/CHG-1/manifest.yml"},
            }),
            text=True,
            capture_output=True,
            check=True,
        )
    finally:
        script_path.unlink(missing_ok=True)
    assert json.loads(result.stdout)["permissionDecision"] == "allow"


def test_github_copilot_hook_denies_direct_review_metadata_edits() -> None:
    projection = GitHubCopilotDriver().project(_context())
    script = next(
        artifact.content
        for artifact in projection.artifacts
        if artifact.path.endswith("forge-review-control.sh")
    )
    script_path = Path(__file__).with_name("forge-review-control.sh")
    script_path.write_text(script, encoding="utf-8")
    try:
        result = subprocess.run(
            ["/bin/sh", str(script_path)],
            input=json.dumps({
                "toolName": "edit",
                "toolArgs": {"file_path": ".forge/changes/CHG-1/review.md"},
            }),
            text=True,
            capture_output=True,
            check=True,
        )
    finally:
        script_path.unlink(missing_ok=True)
    assert json.loads(result.stdout)["permissionDecision"] == "deny"


def test_github_copilot_publication_root_is_fixed_to_github() -> None:
    validate_publication_root(".github")
    with pytest.raises(ValueError):
        validate_publication_root(".github/hooks")


def test_github_copilot_is_registered() -> None:
    assert build_packaged_registry().get("github-copilot").default_target == ".github"
