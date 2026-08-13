from forge_cli.adapters.plan import OperationIntent
from forge_cli.adapters.state import AdapterInstallationRecord, GeneratedArtifact


def _record() -> AdapterInstallationRecord:
    return AdapterInstallationRecord(
        adapter_id="cursor",
        adapter_version="1.0.0",
        harness="cursor",
        protocol_min=1,
        protocol_max_exclusive=2,
        generated_artifacts=(
            GeneratedArtifact(path=".cursor/rules/a.md", digest="a" * 64),
            GeneratedArtifact(path=".cursor/rules/b.md", digest="b" * 64),
        ),
        limitations=(),
    )


def test_matching_recorded_generated_artifacts_have_no_drift() -> None:
    from forge_cli.adapters import ownership

    assert hasattr(ownership, "detect_generated_drift"), "Generated drift detection is not implemented yet"

    findings = ownership.detect_generated_drift(
        _record(),
        {
            ".cursor/rules/a.md": "a" * 64,
            ".cursor/rules/b.md": "b" * 64,
        },
    )

    assert findings == ()


def test_modified_generated_artifact_is_reported_deterministically() -> None:
    from forge_cli.adapters import ownership

    assert hasattr(ownership, "detect_generated_drift"), "Generated drift detection is not implemented yet"

    findings = ownership.detect_generated_drift(
        _record(),
        {
            ".cursor/rules/a.md": "f" * 64,
            ".cursor/rules/b.md": "b" * 64,
        },
    )

    assert len(findings) == 1
    assert findings[0].path == ".cursor/rules/a.md"
    assert findings[0].kind.value == "modified"
    assert findings[0].expected_digest == "a" * 64
    assert findings[0].observed_digest == "f" * 64


def test_missing_generated_artifact_is_reported_as_drift() -> None:
    from forge_cli.adapters import ownership

    assert hasattr(ownership, "detect_generated_drift"), "Generated drift detection is not implemented yet"

    findings = ownership.detect_generated_drift(
        _record(),
        {
            ".cursor/rules/a.md": None,
            ".cursor/rules/b.md": "b" * 64,
        },
    )

    assert len(findings) == 1
    assert findings[0].kind.value == "missing"
    assert findings[0].observed_digest is None


def test_recorded_forge_owned_drift_forces_conflict_before_update() -> None:
    from forge_cli.adapters import ownership

    assert hasattr(ownership, "classify_recorded_forge_owned"), "Recorded Forge-owned classification is not implemented yet"

    decision = ownership.classify_recorded_forge_owned(
        expected_digest="a" * 64,
        exists=True,
        current_digest="f" * 64,
    )

    assert decision.intent is OperationIntent.CONFLICT
    assert decision.safe_to_apply is False
