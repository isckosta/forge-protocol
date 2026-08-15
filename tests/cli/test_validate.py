import json
import shutil
import subprocess
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from typer.testing import CliRunner

from forge_cli.app import app


runner = CliRunner()
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CHANGE_SCHEMA = REPOSITORY_ROOT / "protocol" / "schemas" / "change.schema.json"
CHANGE_SCHEMA_V2 = REPOSITORY_ROOT / "protocol" / "schemas" / "change-v2.schema.json"


def _init_git_repository(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)


def _write_valid_project_configuration(project_root: Path) -> None:
    forge_dir = project_root / ".forge"
    forge_dir.mkdir(parents=True)
    (forge_dir / "forge.yml").write_text(
        "schema: forge/project@1\n"
        "project:\n"
        "  name: example\n"
        "forge:\n"
        "  protocol: 1\n"
        "flows:\n"
        "  default: standard\n"
        "  allow_fast: true\n"
        "  auto_escalation: true\n"
        "testing:\n"
        "  approach: tdd_first\n"
        "review:\n"
        "  strict: true\n"
        "documentation:\n"
        "  impact_evaluation: required\n",
        encoding="utf-8",
    )


def _base_execution_context_manifest() -> dict:
    return yaml.safe_load((FIXTURES / "full-change-agent-same-session.yml").read_text(encoding="utf-8"))


def _write_change(project_root: Path, manifest: dict, slug: str) -> None:
    change_dir = project_root / ".forge" / "changes" / slug
    change_dir.mkdir(parents=True)
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def test_validate_reports_success_for_valid_forge_project(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_valid_project_configuration(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 0
    assert "Forge project is valid" in result.stdout


def test_validate_reports_not_initialized_with_exit_code_two(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2
    assert "E_FORGE_NOT_INITIALIZED" in result.stdout
    assert ".forge/" in result.stdout


def test_full_execution_context_fixture_is_structurally_valid() -> None:
    # Structural layer: forge/change@2 owns the provider-independent execution/context
    # evidence shape. Semantic C-026 equality checks belong to forge validate.
    schema = json.loads(CHANGE_SCHEMA_V2.read_text(encoding="utf-8"))
    manifest = _base_execution_context_manifest()

    Draft202012Validator(schema).validate(manifest)


def test_full_pending_review_without_reviewer_identity_is_structurally_invalid() -> None:
    schema = json.loads(CHANGE_SCHEMA_V2.read_text(encoding="utf-8"))
    manifest = _base_execution_context_manifest()
    manifest["review"]["status"] = "pending"
    manifest["review"].pop("reviewer_identity")

    errors = list(Draft202012Validator(schema).iter_errors(manifest))

    assert any(error.validator == "required" and "reviewer_identity" in error.message for error in errors)


def test_forge_change_v1_does_not_require_reviewer_identity_for_full() -> None:
    schema = json.loads(CHANGE_SCHEMA.read_text(encoding="utf-8"))
    manifest = _base_execution_context_manifest()
    manifest["schema"] = "forge/change@1"
    manifest["review"].pop("reviewer_identity")

    Draft202012Validator(schema).validate(manifest)


def test_validate_rejects_distinct_execution_ids_that_share_context(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_valid_project_configuration(tmp_path)
    manifest = _base_execution_context_manifest()
    _write_change(tmp_path, manifest, "CHG-9999-invalid-shared-context")
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "context" in result.stdout.lower()


def test_validate_rejects_shared_execution_even_with_distinct_context_ids(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_valid_project_configuration(tmp_path)
    manifest = _base_execution_context_manifest()
    identity = manifest["review"]["reviewer_identity"]
    identity["context_id"] = "review-context-001"
    identity["resolver_context_id"] = "resolver-context-001"
    identity["execution_id"] = "shared-execution-001"
    identity["resolver_execution_id"] = "shared-execution-001"
    _write_change(tmp_path, manifest, "CHG-9998-invalid-shared-execution")
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "execution" in result.stdout.lower()


def test_validate_accepts_independent_execution_and_context(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_valid_project_configuration(tmp_path)
    manifest = _base_execution_context_manifest()
    identity = manifest["review"]["reviewer_identity"]
    identity["context_id"] = "review-context-001"
    identity["resolver_context_id"] = "resolver-context-001"
    _write_change(tmp_path, manifest, "CHG-9997-valid-independent-review")
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 0
    assert "Forge project is valid" in result.stdout
