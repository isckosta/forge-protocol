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


def _write_full_same_session_change(project_root: Path) -> None:
    change_dir = project_root / ".forge" / "changes" / "CHG-9999-invalid-same-session-review"
    change_dir.mkdir(parents=True)
    shutil.copyfile(FIXTURES / "full-change-agent-same-session.yml", change_dir / "manifest.yml")


def _write_full_isolated_actor_with_identical_session_refs(project_root: Path) -> None:
    manifest = yaml.safe_load((FIXTURES / "full-change-agent-same-session.yml").read_text(encoding="utf-8"))
    manifest["review"]["reviewer_identity"]["actor_type"] = "agent_isolated_session"
    change_dir = project_root / ".forge" / "changes" / "CHG-9998-invalid-identical-session-refs"
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


def test_full_same_session_red_fixture_is_structurally_valid() -> None:
    # Structural layer: JSON Schema checks presence/types only. This exact RED fixture must pass here
    # so its forge validate failure proves the independent semantic C-026 layer is what rejected it.
    # The fixture declares forge/change@2: the schema suffix that carries the mandatory FULL
    # reviewer_identity requirement (see compatibility.md). forge/change@1 is untouched so that
    # every previously valid Change manifest, including historical ones, remains valid.
    schema = json.loads(CHANGE_SCHEMA_V2.read_text(encoding="utf-8"))
    manifest = yaml.safe_load((FIXTURES / "full-change-agent-same-session.yml").read_text(encoding="utf-8"))

    Draft202012Validator(schema).validate(manifest)


def test_full_pending_review_without_reviewer_identity_is_structurally_invalid() -> None:
    # Structural layer: every forge/change@2 FULL manifest requires a complete reviewer_identity
    # object, independent of review status. Semantic independence strength is checked separately.
    schema = json.loads(CHANGE_SCHEMA_V2.read_text(encoding="utf-8"))
    manifest = yaml.safe_load((FIXTURES / "full-change-agent-same-session.yml").read_text(encoding="utf-8"))
    manifest["review"]["status"] = "pending"
    manifest["review"].pop("reviewer_identity")

    errors = list(Draft202012Validator(schema).iter_errors(manifest))

    assert any(error.validator == "required" and "reviewer_identity" in error.message for error in errors)


def test_forge_change_v1_does_not_require_reviewer_identity_for_full() -> None:
    # Regression guard: forge/change@1 MUST stay backward compatible per compatibility.md
    # ("optional fields... whose absence preserves existing meaning"). A FULL manifest with no
    # reviewer_identity and no review evidence at all must remain structurally valid under v1,
    # or every historical FULL Change manifest becomes retroactively invalid (forbidden by
    # FR-012/INV-001 and by C-045/C-046).
    schema = json.loads(CHANGE_SCHEMA.read_text(encoding="utf-8"))
    manifest = yaml.safe_load((FIXTURES / "full-change-agent-same-session.yml").read_text(encoding="utf-8"))
    manifest["schema"] = "forge/change@1"
    manifest["review"].pop("reviewer_identity")

    Draft202012Validator(schema).validate(manifest)


def test_validate_rejects_full_change_reviewed_in_same_session(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_valid_project_configuration(tmp_path)
    _write_full_same_session_change(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "agent_same_session" in result.stdout


def test_validate_rejects_claimed_isolation_with_identical_session_refs(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_valid_project_configuration(tmp_path)
    _write_full_isolated_actor_with_identical_session_refs(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "identical" in result.stdout
