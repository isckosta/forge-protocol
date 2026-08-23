from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pytest
import yaml
from typer.testing import CliRunner

import forge_cli.app as app_module
from forge_cli.experience.configuration import (
    ExperienceConfigurationError,
    ExperienceReportingConfiguration,
    load_experience_configuration,
)
from forge_cli.experience.model import ExperienceInputError, ObservationInput, parse_record_input
from forge_cli.experience.storage import ExperienceStorage, ExperienceStorageError


def test_experience_reporting_is_disabled_when_contributor_config_is_absent(tmp_path: Path) -> None:
    configuration = load_experience_configuration(tmp_path)

    assert configuration == ExperienceReportingConfiguration(enabled=False)


def test_invalid_contributor_configuration_does_not_enable_reporting(tmp_path: Path) -> None:
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "contributor.yml").write_text(
        "schema: forge/contributor@1\nexperience_reporting: true\n",
        encoding="utf-8",
    )

    with pytest.raises(ExperienceConfigurationError):
        load_experience_configuration(tmp_path)


def test_record_input_preserves_uncertain_observation_fields() -> None:
    record = parse_record_input(
        {
            "observation": {
                "area": "plan-approval",
                "classification": "uncertain",
                "expected": "The Harness should stop after Plan generation.",
                "observed": "The execution continued into Implementation.",
                "evidence": ["The next stage started without a recorded approval."],
                "impact": "The cause was not yet isolated.",
                "workaround": "The user manually interrupted execution.",
                "follow_up": "Investigate Forge, Harness, Adapter, and project causes.",
            }
        }
    )

    assert isinstance(record, ObservationInput)
    assert record.classification == "uncertain"
    assert record.expected != record.observed


def test_project_problem_is_not_rewritten_as_forge_problem() -> None:
    record = parse_record_input(
        {
            "observation": {
                "area": "application-validation",
                "classification": "project_problem",
                "expected": "The application rejects invalid input.",
                "observed": "The application accepted invalid input.",
                "evidence": ["Project test reproduced the acceptance."],
                "impact": "The project behavior is incorrect.",
            }
        }
    )

    assert record.classification == "project_problem"


def test_first_observation_lazily_creates_a_report_with_safe_context(tmp_path: Path) -> None:
    storage = ExperienceStorage(
        tmp_path,
        context={"forge_version": "0.1.0a2", "protocol": 2, "commit": "abc123"},
    )
    observation = parse_record_input(
        {
            "observation": {
                "area": "doctor",
                "classification": "forge_problem",
                "expected": "Doctor explains the invalid Adapter state.",
                "observed": "Doctor returned no actionable explanation.",
                "evidence": ["The command exited without a diagnostic."],
                "impact": "The contributor could not diagnose the state.",
            }
        }
    )

    path = storage.record(observation)

    assert path == tmp_path / "dogfooding" / "reports" / "FER-0001.yml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert document["schema"] == "forge/experience-report@1"
    assert document["source"]["commit"] == "abc123"
    assert document["observations"][0]["id"] == "FER-0001-O001"
    markdown_path = path.with_suffix(".md")
    assert markdown_path.is_file()
    assert "# FER-0001" in markdown_path.read_text(encoding="utf-8")


def test_record_updates_markdown_projection_when_appending_evidence(tmp_path: Path) -> None:
    storage = ExperienceStorage(tmp_path, context={})
    positive = parse_record_input(
        {"positive_evidence": {"area": "doctor", "observed": "Doctor worked."}}
    )

    path = storage.record(positive)
    storage.record(
        parse_record_input(
            {
                "observation": {
                    "area": "storage",
                    "classification": "uncertain",
                    "expected": "The report remains readable.",
                    "observed": "The report was updated.",
                    "evidence": ["The Markdown projection contains the entry."],
                    "impact": "Review remains possible.",
                }
            }
        )
    )

    rendered = path.with_suffix(".md").read_text(encoding="utf-8")
    assert "## Positive Evidence" in rendered
    assert "## Observations" in rendered
    assert "FER-0001-O001" in rendered


def test_markdown_write_failure_preserves_canonical_report(tmp_path: Path, monkeypatch) -> None:
    storage = ExperienceStorage(tmp_path, context={})
    entry = parse_record_input(
        {"positive_evidence": {"area": "storage", "observed": "Canonical data was written."}}
    )

    def fail_markdown(path: Path, content: str) -> None:
        raise OSError("simulated Markdown disk failure")

    monkeypatch.setattr(storage, "_atomic_write_markdown", fail_markdown)

    with pytest.raises(ExperienceStorageError, match="simulated Markdown disk failure"):
        storage.record(entry)

    canonical = tmp_path / "dogfooding" / "reports" / "FER-0001.yml"
    assert canonical.is_file()
    assert yaml.safe_load(canonical.read_text(encoding="utf-8"))["positive_evidence"][0]["id"] == "FER-0001-P001"


def test_positive_evidence_can_create_a_report_without_an_observation(tmp_path: Path) -> None:
    storage = ExperienceStorage(tmp_path, context={"protocol": "unknown"})
    positive = parse_record_input(
        {"positive_evidence": {"area": "change-scaffolding", "observed": "The scaffold was valid."}}
    )

    path = storage.record(positive)

    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert document["observations"] == []
    assert document["positive_evidence"][0]["id"] == "FER-0001-P001"


def test_report_ids_are_not_reused_when_a_report_already_exists(tmp_path: Path) -> None:
    reports = tmp_path / "dogfooding" / "reports"
    reports.mkdir(parents=True)
    (reports / "FER-0001.yml").write_text("existing: true\n", encoding="utf-8")
    storage = ExperienceStorage(tmp_path, context={})
    positive = parse_record_input(
        {"positive_evidence": {"area": "doctor", "observed": "Doctor worked."}}
    )

    path = storage.record(positive)

    assert path.name == "FER-0002.yml"


def test_concurrent_observations_on_one_report_are_all_preserved(tmp_path: Path) -> None:
    storage = ExperienceStorage(tmp_path, context={})

    def record(index: int) -> Path:
        return storage.record(
            parse_record_input(
                {
                    "observation": {
                        "area": "concurrency",
                        "classification": "uncertain",
                        "expected": "All observations remain durable.",
                        "observed": f"Observation {index} was recorded.",
                        "evidence": [f"evidence-{index}"],
                        "impact": "Concurrent evidence must not be lost.",
                    }
                }
            )
        )

    with ThreadPoolExecutor(max_workers=6) as executor:
        paths = list(executor.map(record, range(6)))

    document = yaml.safe_load(paths[0].read_text(encoding="utf-8"))
    assert len(document["observations"]) == 6


def test_experience_cli_is_explicit_and_disabled_by_default(tmp_path: Path, monkeypatch) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(app_module.app, ["experience", "status"])

    assert result.exit_code == 0
    assert "disabled" in result.stdout.lower()
    assert not (tmp_path / "dogfooding").exists()


def test_experience_cli_records_structured_input_after_explicit_enablement(
    tmp_path: Path, monkeypatch
) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    assert runner.invoke(app_module.app, ["init"]).exit_code == 0
    assert runner.invoke(app_module.app, ["experience", "enable"]).exit_code == 0
    input_path = tmp_path / "observation.yml"
    input_path.write_text(
        "observation:\n"
        "  area: doctor\n"
        "  classification: forge_problem\n"
        "  expected: Doctor explains the problem.\n"
        "  observed: Doctor did not explain the problem.\n"
        "  evidence: [The command returned no actionable message.]\n"
        "  impact: Diagnosis was delayed.\n",
        encoding="utf-8",
    )

    result = runner.invoke(app_module.app, ["experience", "record", "--input", str(input_path)])

    assert result.exit_code == 0, result.stdout
    assert "Forge experience report recorded:" in result.stdout
    assert (tmp_path / "dogfooding" / "reports" / "FER-0001.yml").is_file()


def test_experience_cli_can_append_to_the_report_returned_by_the_first_record(
    tmp_path: Path, monkeypatch
) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    assert runner.invoke(app_module.app, ["init"]).exit_code == 0
    assert runner.invoke(app_module.app, ["experience", "enable"]).exit_code == 0
    input_path = tmp_path / "observation.yml"
    input_path.write_text(
        "positive_evidence:\n  area: doctor\n  observed: Doctor worked.\n",
        encoding="utf-8",
    )
    first = runner.invoke(app_module.app, ["experience", "record", "--input", str(input_path)])
    second = runner.invoke(
        app_module.app,
        ["experience", "record", "--input", str(input_path), "--report", "FER-0001"],
    )

    assert first.exit_code == 0
    assert second.exit_code == 0, second.stdout
    document = yaml.safe_load(
        (tmp_path / "dogfooding" / "reports" / "FER-0001.yml").read_text(encoding="utf-8")
    )
    assert len(document["positive_evidence"]) == 2


def test_experience_cli_renders_existing_report_without_enablement(tmp_path: Path, monkeypatch) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "dogfooding" / "reports"
    reports.mkdir(parents=True)
    (reports / "FER-0001.yml").write_text(
        "schema: forge/experience-report@1\n"
        "report: FER-0001\n"
        "source: {protocol: 2}\n"
        "observations: []\n"
        "positive_evidence:\n"
        "  - {id: FER-0001-P001, area: doctor, observed: Doctor worked.}\n"
        "follow_up_candidates: []\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(app_module.app, ["experience", "render", "FER-0001"])

    assert result.exit_code == 0, result.stdout
    assert "rendered" in result.stdout.lower()
    assert "## Positive Evidence" in (reports / "FER-0001.md").read_text(encoding="utf-8")


def test_experience_cli_render_all_repairs_drift_deterministically(tmp_path: Path, monkeypatch) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "dogfooding" / "reports"
    reports.mkdir(parents=True)
    (reports / "FER-0001.yml").write_text(
        "schema: forge/experience-report@1\n"
        "report: FER-0001\n"
        "source: {}\n"
        "observations: []\npositive_evidence: []\nfollow_up_candidates: []\n",
        encoding="utf-8",
    )
    projection = reports / "FER-0001.md"
    projection.write_text("manual drift\n", encoding="utf-8")

    first = CliRunner().invoke(app_module.app, ["experience", "render", "--all"])
    rendered = projection.read_text(encoding="utf-8")
    second = CliRunner().invoke(app_module.app, ["experience", "render", "--all"])

    assert first.exit_code == 0, first.stdout
    assert second.exit_code == 0, second.stdout
    assert rendered == projection.read_text(encoding="utf-8")
    assert "manual drift" not in rendered


def test_experience_cli_render_rejects_report_path_traversal(tmp_path: Path, monkeypatch) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "dogfooding" / "reports"
    reports.mkdir(parents=True)
    outside = tmp_path / "outside.yml"
    outside.write_text(
        "schema: forge/experience-report@1\n"
        "report: outside\n"
        "source: {}\n"
        "observations: []\npositive_evidence: []\nfollow_up_candidates: []\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(app_module.app, ["experience", "render", "../../outside"])

    assert result.exit_code == 2
    assert "invalid" in result.stdout.lower()
    assert not outside.with_suffix(".md").exists()


def test_experience_cli_render_rejects_a_symlinked_dogfooding_ancestor(
    tmp_path: Path, monkeypatch
) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / "dogfooding").symlink_to(outside, target_is_directory=True)

    result = CliRunner().invoke(app_module.app, ["experience", "render", "FER-0001"])

    assert result.exit_code == 2
    assert "invalid" in result.stdout.lower()


def test_experience_cli_render_rejects_missing_explicit_report(tmp_path: Path, monkeypatch) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "dogfooding" / "reports").mkdir(parents=True)

    result = CliRunner().invoke(app_module.app, ["experience", "render", "FER-0001"])

    assert result.exit_code == 2
    assert "missing" in result.stdout.lower()


def test_report_write_failure_is_explicit_and_does_not_touch_change_state(tmp_path: Path, monkeypatch) -> None:
    storage = ExperienceStorage(tmp_path, context={})
    entry = parse_record_input(
        {"positive_evidence": {"area": "storage", "observed": "A write was attempted."}}
    )

    def fail_write(path, document):
        raise OSError("simulated disk failure")

    monkeypatch.setattr(storage, "_atomic_write", fail_write)

    with pytest.raises(ExperienceStorageError, match="simulated disk failure"):
        storage.record(entry)

    assert not (tmp_path / ".forge" / "changes").exists()


def test_experience_validate_rejects_a_malformed_report(tmp_path: Path, monkeypatch) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "dogfooding" / "reports"
    reports.mkdir(parents=True)
    (reports / "FER-0001.yml").write_text(
        "schema: forge/experience-report@1\nreport: FER-0001\nobservations: nope\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(app_module.app, ["experience", "validate"])

    assert result.exit_code == 2
    assert "invalid" in result.stdout.lower()


def test_record_rejects_obvious_secret_material() -> None:
    with pytest.raises(ExperienceInputError, match="sensitive"):
        parse_record_input(
            {
                "observation": {
                    "area": "security",
                    "classification": "uncertain",
                    "expected": "The token remains private.",
                    "observed": "Authorization: Bearer very-secret-token",
                    "evidence": ["Bearer very-secret-token"],
                    "impact": "A secret could be exposed.",
                }
            }
        )


def test_record_rejects_secret_and_oversized_evidence_items() -> None:
    with pytest.raises(ExperienceInputError, match="sensitive"):
        parse_record_input(
            {
                "observation": {
                    "area": "security",
                    "classification": "uncertain",
                    "expected": "Evidence is safe.",
                    "observed": "The evidence is sensitive.",
                    "evidence": ["Authorization: Bearer very-secret-token"],
                    "impact": "The evidence must be rejected.",
                }
            }
        )
    with pytest.raises(ExperienceInputError, match="concise"):
        parse_record_input(
            {
                "observation": {
                    "area": "size",
                    "classification": "uncertain",
                    "expected": "Evidence is concise.",
                    "observed": "The evidence is too large.",
                    "evidence": ["x" * 2001],
                    "impact": "The evidence must be rejected.",
                }
            }
        )


def test_record_rejects_unbounded_prompt_sized_text() -> None:
    with pytest.raises(ExperienceInputError, match="concise"):
        parse_record_input(
            {
                "observation": {
                    "area": "interaction",
                    "classification": "uncertain",
                    "expected": "A concise report entry.",
                    "observed": "x" * 2001,
                    "evidence": ["short evidence"],
                    "impact": "The entry is too large.",
                }
            }
        )


def test_recording_to_a_malformed_existing_report_returns_storage_error(tmp_path: Path) -> None:
    reports = tmp_path / "dogfooding" / "reports"
    reports.mkdir(parents=True)
    (reports / "FER-0001.yml").write_text(
        "schema: forge/experience-report@1\nreport: FER-0001\nsource: {}\n",
        encoding="utf-8",
    )
    storage = ExperienceStorage(tmp_path, context={}, report_id="FER-0001")
    entry = parse_record_input(
        {"positive_evidence": {"area": "storage", "observed": "A malformed report was found."}}
    )

    with pytest.raises(ExperienceStorageError, match="invalid"):
        storage.record(entry)


def test_recording_rejects_a_symlinked_report_path(tmp_path: Path) -> None:
    reports = tmp_path / "dogfooding" / "reports"
    reports.mkdir(parents=True)
    target = tmp_path / "secret.yml"
    target.write_text("source: {token: SECRET}\n", encoding="utf-8")
    (reports / "FER-0001.yml").symlink_to(target)
    storage = ExperienceStorage(tmp_path, context={}, report_id="FER-0001")
    entry = parse_record_input(
        {"positive_evidence": {"area": "storage", "observed": "A symlink was found."}}
    )

    with pytest.raises(ExperienceStorageError, match="does not exist"):
        storage.record(entry)


def test_experience_validate_rejects_a_malformed_entry(tmp_path: Path, monkeypatch) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "dogfooding" / "reports"
    reports.mkdir(parents=True)
    (reports / "FER-0001.yml").write_text(
        "schema: forge/experience-report@1\nreport: FER-0001\nsource: {}\n"
        "observations: [not-a-mapping]\npositive_evidence: []\nfollow_up_candidates: []\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(app_module.app, ["experience", "validate"])

    assert result.exit_code == 2


def test_recording_rejects_a_symlinked_dogfooding_ancestor(tmp_path: Path) -> None:
    target = tmp_path / "outside"
    target.mkdir()
    (tmp_path / "dogfooding").symlink_to(target, target_is_directory=True)
    storage = ExperienceStorage(tmp_path, context={})
    entry = parse_record_input(
        {"positive_evidence": {"area": "storage", "observed": "An ancestor was symlinked."}}
    )

    with pytest.raises(ExperienceStorageError, match="safe directory"):
        storage.record(entry)


def test_experience_validate_rejects_unstructured_follow_up_candidates(tmp_path: Path, monkeypatch) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "dogfooding" / "reports"
    reports.mkdir(parents=True)
    (reports / "FER-0001.yml").write_text(
        "schema: forge/experience-report@1\nreport: FER-0001\nsource: {}\n"
        "observations: []\npositive_evidence: []\nfollow_up_candidates: [42]\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(app_module.app, ["experience", "validate"])

    assert result.exit_code == 2


def test_experience_validate_rejects_symlinked_report_files(tmp_path: Path, monkeypatch) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True, text=True)
    monkeypatch.chdir(tmp_path)
    reports = tmp_path / "dogfooding" / "reports"
    reports.mkdir(parents=True)
    target = tmp_path / "outside.yml"
    target.write_text(
        "schema: forge/experience-report@1\nreport: FER-0001\nsource: {}\n"
        "observations: []\npositive_evidence: []\nfollow_up_candidates: []\n",
        encoding="utf-8",
    )
    (reports / "FER-0001.yml").symlink_to(target)

    result = CliRunner().invoke(app_module.app, ["experience", "validate"])

    assert result.exit_code == 2
