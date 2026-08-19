import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator
from typer.testing import CliRunner

from forge_cli.app import app


runner = CliRunner()
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CHANGE_SCHEMA = REPOSITORY_ROOT / "protocol" / "schemas" / "change.schema.json"
CHANGE_SCHEMA_V2 = REPOSITORY_ROOT / "protocol" / "schemas" / "change-v2.schema.json"
PROVENANCE_SCHEMA = REPOSITORY_ROOT / "protocol" / "schemas" / "execution-provenance.schema.json"


def _init_git_repository(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)


def _write_project_configuration(project_root: Path, protocol: int = 1) -> None:
    forge_dir = project_root / ".forge"
    forge_dir.mkdir(parents=True, exist_ok=True)
    (forge_dir / "forge.yml").write_text(
        "schema: forge/project@1\n"
        "project:\n"
        "  name: example\n"
        "forge:\n"
        f"  protocol: {protocol}\n"
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


def _base_protocol2_manifest(flow: str = "full", review_status: str = "passed") -> dict:
    return {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": "CHG-9999", "title": "Protocol 2 review", "kind": "feature"},
        "flow": {"initial": flow, "current": flow, "escalations": []},
        "state": {"current": "strict_review"},
        "artifacts": {},
        "tdd": {"status": "compliant", "cycles": 1},
        "verification": {"status": "passed"},
        "review": {
            "status": review_status,
            "iteration": 1,
            "blockers": 0,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "iterations": [
                {
                    "id": "review-001",
                    "revision": "revision-a",
                    "subject_provenance": "implementation-001",
                    "reviewer_provenance": "review-001",
                    "status": review_status,
                }
            ],
        },
        "documentation": {"impact_evaluated": True, "update_required": False},
    }


def _base_provenance(
    *,
    subject_role: str = "implementation",
    subject_revision: str = "revision-a",
    subject_execution: str = "implementation-exec-001",
    subject_context: str = "implementation-context-001",
    review_execution: str = "review-exec-001",
    review_context: str = "review-context-001",
) -> dict:
    return {
        "schema": "forge/execution-provenance@1",
        "change": "CHG-9999",
        "records": [
            {
                "id": "implementation-001",
                "role": subject_role,
                "execution": {"id": subject_execution, "context_id": subject_context},
                "recorded_at": "2026-08-15T18:30:00Z",
                "revision": {"id": subject_revision, "commit": "a" * 40},
                "source": {"assurance": "recorded", "observed_by": "self"},
            },
            {
                "id": "review-001",
                "role": "review",
                "execution": {"id": review_execution, "context_id": review_context},
                "recorded_at": "2026-08-15T18:31:00Z",
                "revision": {"id": subject_revision, "commit": "a" * 40},
                "source": {"assurance": "recorded", "observed_by": "self"},
            },
        ],
    }


def _write_change(project_root: Path, manifest: dict, slug: str, provenance: dict | None = None) -> None:
    change_dir = project_root / ".forge" / "changes" / slug
    change_dir.mkdir(parents=True)
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    if provenance is not None:
        (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")


def _invoke_validate(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return runner.invoke(app, ["validate"])


def test_validate_reports_success_for_valid_protocol1_project(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=1)

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 0
    assert "Forge project is valid" in result.stdout


def test_validate_reports_not_initialized_with_exit_code_two(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2
    assert "E_FORGE_NOT_INITIALIZED" in result.stdout
    assert ".forge/" in result.stdout


def test_protocol1_preserves_pre_chg0008_review_semantics(tmp_path: Path, monkeypatch) -> None:
    """Protocol 1 must not retroactively require execution provenance."""
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=1)
    manifest = _base_protocol2_manifest()
    manifest.pop("protocol")
    manifest["schema"] = "forge/change@1"
    manifest["review"].pop("iterations")
    _write_change(tmp_path, manifest, "CHG-9999-protocol1-legacy")

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 0
    assert "C-026" not in result.stdout


@pytest.mark.parametrize("flow", ["fast", "standard", "full"])
def test_protocol2_review_passed_requires_recorded_provenance_for_every_flow(
    tmp_path: Path, monkeypatch, flow: str
) -> None:
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=2)
    _write_change(tmp_path, _base_protocol2_manifest(flow=flow), f"CHG-9999-{flow}-missing-provenance")

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "provenance" in result.stdout.lower()


def test_protocol2_rejects_forged_distinct_ids_without_matching_records(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=2)
    manifest = _base_protocol2_manifest()
    manifest["review"]["iterations"][0]["subject_provenance"] = "resolver-exec-fake"
    manifest["review"]["iterations"][0]["reviewer_provenance"] = "review-exec-fake"
    _write_change(tmp_path, manifest, "CHG-9999-forged")

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "not found" in result.stdout.lower() or "provenance" in result.stdout.lower()


def test_protocol2_rejects_review_reference_to_wrong_revision(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=2)
    manifest = _base_protocol2_manifest()
    provenance = _base_provenance(subject_revision="revision-b")
    _write_change(tmp_path, manifest, "CHG-9999-wrong-revision", provenance)

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "revision" in result.stdout.lower()


@pytest.mark.parametrize(
    ("subject_execution", "subject_context", "review_execution", "review_context", "needle"),
    [
        ("shared-exec", "implementation-context", "shared-exec", "review-context", "execution"),
        ("implementation-exec", "shared-context", "review-exec", "shared-context", "context"),
    ],
)
def test_protocol2_rejects_shared_execution_or_context(
    tmp_path: Path,
    monkeypatch,
    subject_execution: str,
    subject_context: str,
    review_execution: str,
    review_context: str,
    needle: str,
) -> None:
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=2)
    provenance = _base_provenance(
        subject_execution=subject_execution,
        subject_context=subject_context,
        review_execution=review_execution,
        review_context=review_context,
    )
    _write_change(tmp_path, _base_protocol2_manifest(), "CHG-9999-shared-boundary", provenance)

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert needle in result.stdout.lower()


@pytest.mark.parametrize("flow", ["fast", "standard", "full"])
def test_protocol2_accepts_independent_recorded_provenance_for_every_flow(
    tmp_path: Path, monkeypatch, flow: str
) -> None:
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=2)
    manifest = _base_protocol2_manifest(flow=flow)
    provenance = _base_provenance()
    _write_change(tmp_path, manifest, f"CHG-9999-{flow}-valid", provenance)

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 0
    assert "Forge project is valid" in result.stdout


def test_protocol2_accepts_execution_provenance_v2_ledger_for_bound_review_iteration(
    tmp_path: Path, monkeypatch
) -> None:
    """CHG-0016 R012 (BLOCKER, Strict Review): C-026's bound-Review-Iteration
    check hard-coded forge/execution-provenance@1 and rejected @2, which
    CHG-0015 introduced and catalogued -- so no Protocol 2 Change using the
    @2 ledger (CHG-0015 or CHG-0016 itself) could ever record a bound Review
    Iteration and remain valid. Widened to accept both, matching
    _validate_delegated_authority's existing set."""
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=2)
    manifest = _base_protocol2_manifest()
    provenance = _base_provenance()
    provenance["schema"] = "forge/execution-provenance@2"
    _write_change(tmp_path, manifest, "CHG-9999-v2-ledger-valid", provenance)

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 0
    assert "Forge project is valid" in result.stdout


def test_protocol2_rereview_must_be_independent_from_resolution_provenance(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=2)
    manifest = _base_protocol2_manifest()
    manifest["review"]["iteration"] = 2
    manifest["review"]["iterations"] = [
        {
            "id": "review-001",
            "revision": "revision-a",
            "subject_provenance": "implementation-001",
            "reviewer_provenance": "review-001",
            "status": "failed",
        },
        {
            "id": "review-002",
            "revision": "revision-b",
            "subject_provenance": "resolution-001",
            "reviewer_provenance": "review-002",
            "status": "passed",
        },
    ]
    provenance = {
        "schema": "forge/execution-provenance@1",
        "change": "CHG-9999",
        "records": [
            {
                "id": "implementation-001",
                "role": "implementation",
                "execution": {"id": "impl-exec", "context_id": "impl-context"},
                "recorded_at": "2026-08-15T18:00:00Z",
                "revision": {"id": "revision-a", "commit": "a" * 40},
                "source": {"assurance": "recorded", "observed_by": "self"},
            },
            {
                "id": "review-001",
                "role": "review",
                "execution": {"id": "review-exec-1", "context_id": "review-context-1"},
                "recorded_at": "2026-08-15T18:01:00Z",
                "revision": {"id": "revision-a", "commit": "a" * 40},
                "source": {"assurance": "recorded", "observed_by": "self"},
            },
            {
                "id": "resolution-001",
                "role": "resolution",
                "execution": {"id": "resolution-exec", "context_id": "resolution-context"},
                "recorded_at": "2026-08-15T18:02:00Z",
                "revision": {"id": "revision-b", "commit": "b" * 40},
                "source": {"assurance": "recorded", "observed_by": "self"},
            },
            {
                "id": "review-002",
                "role": "review",
                "execution": {"id": "review-exec-2", "context_id": "resolution-context"},
                "recorded_at": "2026-08-15T18:03:00Z",
                "revision": {"id": "revision-b", "commit": "b" * 40},
                "source": {"assurance": "recorded", "observed_by": "self"},
            },
        ],
    }
    _write_change(tmp_path, manifest, "CHG-9999-rereview", provenance)

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "context" in result.stdout.lower()


def test_protocol2_rejects_partial_provenance_record(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=2)
    provenance = _base_provenance()
    provenance["records"][0]["execution"].pop("context_id")
    _write_change(tmp_path, _base_protocol2_manifest(), "CHG-9999-partial-provenance", provenance)

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "provenance" in result.stdout.lower() or "context" in result.stdout.lower()


def test_protocol2_active_change_cannot_downgrade_to_change_v1_to_escape_gate(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=2)
    manifest = _base_protocol2_manifest()
    manifest.pop("protocol")
    manifest["schema"] = "forge/change@1"
    manifest["review"].pop("iterations")
    _write_change(tmp_path, manifest, "CHG-9999-downgrade")

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 2
    assert "C-026" in result.stdout
    assert "protocol 2" in result.stdout.lower() or "change@2" in result.stdout.lower()


def test_protocol2_project_preserves_completed_historical_change_v1(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    _write_project_configuration(tmp_path, protocol=2)
    manifest = _base_protocol2_manifest()
    manifest.pop("protocol")
    manifest["schema"] = "forge/change@1"
    manifest["state"]["current"] = "complete"
    manifest["review"].pop("iterations")
    _write_change(tmp_path, manifest, "CHG-0001-historical")

    result = _invoke_validate(tmp_path, monkeypatch)

    assert result.exit_code == 0


def test_change_v1_schema_preserves_historical_shape_without_reviewer_identity() -> None:
    schema = json.loads(CHANGE_SCHEMA.read_text(encoding="utf-8"))
    review_properties = schema["properties"]["review"]["properties"]

    assert "reviewer_identity" not in review_properties


def test_change_v2_schema_models_protocol2_review_iterations() -> None:
    schema = json.loads(CHANGE_SCHEMA_V2.read_text(encoding="utf-8"))
    manifest = _base_protocol2_manifest()

    Draft202012Validator(schema).validate(manifest)


def test_execution_provenance_schema_accepts_complete_recorded_evidence() -> None:
    schema = json.loads(PROVENANCE_SCHEMA.read_text(encoding="utf-8"))

    Draft202012Validator(schema).validate(_base_provenance())
