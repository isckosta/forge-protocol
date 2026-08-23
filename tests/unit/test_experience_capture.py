from pathlib import Path

from forge_cli.experience.capture import ExperienceCapturePolicy, ExperienceEvent
from forge_cli.experience.configuration import write_experience_configuration
from forge_cli.experience.recorder import ExperienceRecorder
from forge_cli.experience.storage import ExperienceStorage, ExperienceStorageError


def test_policy_accepts_named_adapter_conformance_violation_as_uncertain() -> None:
    event = ExperienceEvent(
        event_type="adapter_conformance",
        detector="adapter-conformance",
        expected="Required Forge stage remains represented and enforced.",
        observed="Required Forge stage was removed from the Adapter representation.",
        evidence=("E_FORGE_ADAPTER_STAGE_REMOVED: strict_review",),
        context={"change": "CHG-0035", "boundary": "adapter-conformance"},
    )

    decision = ExperienceCapturePolicy().evaluate(event)

    assert decision.capture is True
    assert decision.classification == "uncertain"
    assert decision.fingerprint


def test_policy_ignores_ordinary_project_failure() -> None:
    event = ExperienceEvent(
        event_type="test_failure",
        detector="pytest",
        expected="Project tests pass.",
        observed="A project test failed.",
        evidence=("project assertion failed",),
        context={},
    )

    decision = ExperienceCapturePolicy().evaluate(event)

    assert decision.capture is False


def test_policy_fingerprint_excludes_volatile_context() -> None:
    base = dict(
        event_type="adapter_conformance",
        detector="adapter-conformance",
        expected="The review gate remains represented.",
        observed="The review gate was removed.",
        evidence=("E_FORGE_ADAPTER_GATE_REMOVED: review_gate",),
    )

    first = ExperienceCapturePolicy().evaluate(
        ExperienceEvent(**base, context={"change": "CHG-0035", "recorded_at": "one"})
    )
    second = ExperienceCapturePolicy().evaluate(
        ExperienceEvent(**base, context={"change": "CHG-0035", "recorded_at": "two"})
    )

    assert first.fingerprint == second.fingerprint


def test_disabled_recorder_does_not_create_report_or_auxiliary_state(tmp_path: Path) -> None:
    event = ExperienceEvent(
        event_type="adapter_conformance",
        detector="adapter-conformance",
        expected="A required gate remains represented.",
        observed="A required gate was removed.",
        evidence=("E_FORGE_ADAPTER_GATE_REMOVED: review_gate",),
        context={"change": "CHG-0035"},
    )

    assert ExperienceRecorder(tmp_path, context={}).capture(event) is None
    assert not (tmp_path / "dogfooding").exists()


def test_recorder_coalesces_equivalent_events(tmp_path: Path) -> None:
    write_experience_configuration(tmp_path, True)
    event = ExperienceEvent(
        event_type="adapter_conformance",
        detector="adapter-conformance",
        expected="A required gate remains represented.",
        observed="A required gate was removed.",
        evidence=("E_FORGE_ADAPTER_GATE_REMOVED: review_gate",),
        context={"change": "CHG-0035"},
    )
    recorder = ExperienceRecorder(tmp_path, context={"change": "CHG-0035"})

    first = recorder.capture(event)
    second = recorder.capture(event)

    assert first is not None
    assert second == first
    import yaml

    document = yaml.safe_load(first.read_text(encoding="utf-8"))
    assert len(document["observations"]) == 1
    assert document["observations"][0]["classification"] == "uncertain"
    assert document["observations"][0]["capture"]["mode"] == "automatic"


def test_recorder_exposes_secondary_failure_without_raising(tmp_path: Path, monkeypatch) -> None:
    write_experience_configuration(tmp_path, True)
    event = ExperienceEvent(
        event_type="adapter_conformance",
        detector="adapter-conformance",
        expected="A required gate remains represented.",
        observed="A required gate was removed.",
        evidence=("E_FORGE_ADAPTER_GATE_REMOVED: review_gate",),
        context={"change": "CHG-0035"},
    )

    def fail(*args, **kwargs):
        raise ExperienceStorageError("injected FER failure")

    monkeypatch.setattr(ExperienceStorage, "record", fail)
    recorder = ExperienceRecorder(tmp_path, context={})

    assert recorder.capture(event) is None
    assert recorder.last_diagnostic == "injected FER failure"


def test_malformed_configuration_does_not_escape_recorder(tmp_path: Path) -> None:
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "contributor.yml").write_text(
        "schema: forge/contributor@1\nexperience_reporting: malformed\n",
        encoding="utf-8",
    )
    event = ExperienceEvent(
        event_type="adapter_conformance",
        detector="adapter-conformance",
        expected="A required gate remains represented.",
        observed="A required gate was removed.",
        evidence=("E_FORGE_ADAPTER_GATE_REMOVED: review_gate",),
        context={"change": "CHG-0035"},
    )

    assert ExperienceRecorder(tmp_path, context={}).capture(event) is None


def test_recorder_deduplicates_across_instances(tmp_path: Path) -> None:
    write_experience_configuration(tmp_path, True)
    event = ExperienceEvent(
        event_type="adapter_conformance",
        detector="adapter-conformance",
        expected="A required gate remains represented.",
        observed="A required gate was removed.",
        evidence=("E_FORGE_ADAPTER_GATE_REMOVED: review_gate",),
        context={"change": "CHG-0035"},
    )

    first = ExperienceRecorder(tmp_path, context={})
    second = ExperienceRecorder(tmp_path, context={})
    first_path = first.capture(event)
    second_path = second.capture(event)

    assert second_path == first_path
    assert len(list((tmp_path / "dogfooding" / "reports").glob("FER-*.yml"))) == 1


def test_secondary_diagnostic_remains_non_raising_when_warnings_are_errors(
    tmp_path: Path, monkeypatch, recwarn
) -> None:
    write_experience_configuration(tmp_path, True)
    event = ExperienceEvent(
        event_type="adapter_conformance",
        detector="adapter-conformance",
        expected="A required gate remains represented.",
        observed="A required gate was removed.",
        evidence=("E_FORGE_ADAPTER_GATE_REMOVED: review_gate",),
        context={"change": "CHG-0035"},
    )

    def fail(*args, **kwargs):
        raise ExperienceStorageError("injected FER failure")

    monkeypatch.setattr(ExperienceStorage, "record", fail)
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert ExperienceRecorder(tmp_path, context={}).capture(event) is None
