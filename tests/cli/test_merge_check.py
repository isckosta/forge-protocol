from typer.testing import CliRunner
import subprocess
import yaml

from forge_cli.app import app


runner = CliRunner()


def _commit(root, message: str) -> str:
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", message], cwd=root, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def _manifest(status: str = "complete", review_status: str = "passed") -> dict:
    return {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": "CHG-9001", "title": "Fixture", "kind": "bugfix"},
        "flow": {"initial": "standard", "current": "standard", "escalations": []},
        "state": {"current": status},
        "artifacts": {"intent": "complete", "discovery": "complete", "specification": "complete", "inspection": "complete", "test_design": "complete", "plan": "complete", "tdd_evidence": "complete", "verification": "complete", "review": "complete", "documentation": "complete"},
        "tdd": {"status": "compliant", "cycles": 1},
        "verification": {"status": "passed"},
        "review": {
            "status": review_status,
            "iteration": 1,
            "blockers": 0,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "iterations": [{"id": "review-001", "revision": "fixture", "status": "passed", "subject_provenance": "impl-001", "reviewer_provenance": "review-001"}],
        },
        "documentation": {"impact_evaluated": True, "update_required": False},
    }


def test_merge_check_reports_blocked_readiness_with_distinct_exit_code(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=tmp_path, check=True)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.strip()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "runtime.py").write_text("value = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "src/runtime.py"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "material change"], cwd=tmp_path, check=True)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.strip()

    result = runner.invoke(
        app,
        [
            "change",
            "merge-check",
            "--base",
            base,
            "--head",
            head,
        ],
    )

    assert result.exit_code == 1
    assert "MERGE BLOCKED" in result.stdout


def test_merge_check_blocks_incomplete_lifecycle_claim(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9001-fixture"
    change_dir.mkdir(parents=True)
    (change_dir / "manifest.yml").write_text(
        yaml.safe_dump(_manifest(status="review", review_status="pending"), sort_keys=False),
        encoding="utf-8",
    )
    head = _commit(tmp_path, "record pending Change")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert result.exit_code == 1
    assert "MR-004" in result.stdout
    assert "MR-005" in result.stdout


def test_merge_check_mr_004_label_is_profile_neutral(tmp_path, monkeypatch) -> None:
    """CHG-0048 TDD-013: MR-004's diagnostic label must not say "Strict
    Review" -- Review is no longer synonymous with the strict profile."""
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9001-fixture"
    change_dir.mkdir(parents=True)
    (change_dir / "manifest.yml").write_text(
        yaml.safe_dump(_manifest(status="review", review_status="pending"), sort_keys=False),
        encoding="utf-8",
    )
    head = _commit(tmp_path, "record pending Change")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert result.exit_code == 1
    assert "MR-004" in result.stdout
    assert "strict review" not in result.stdout.lower()


def test_merge_check_accepts_complete_change_without_material_runtime_diff(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9001-fixture"
    change_dir.mkdir(parents=True)
    (change_dir / "manifest.yml").write_text(
        yaml.safe_dump(_manifest(), sort_keys=False), encoding="utf-8"
    )
    (change_dir / "verification.md").write_text("## Result\n\n**PASS**\n", encoding="utf-8")
    (change_dir / "review.md").write_text("## Verdict\n\n**PASS**\n", encoding="utf-8")
    subject = _commit(tmp_path, "freeze complete Change subject")
    provenance = {"schema": "forge/execution-provenance@2", "change": "CHG-9001", "records": [
        {"id": "impl-001", "role": "implementation", "execution": {"id": "impl", "context_id": "impl-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "implementation-subject", "statement": "Fixture implementation subject."}},
        {"id": "review-001", "role": "review", "execution": {"id": "review", "context_id": "review-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "strict-review", "statement": "Fixture independent review."}},
        {"id": "verification-001", "role": "implementation", "execution": {"id": "verification", "context_id": "verification-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "verification.md", "statement": "Fixture verification evidence."}},
    ]}
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    head = _commit(tmp_path, "record review-control metadata")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert result.exit_code == 0, result.stdout
    assert "MERGE READY" in result.stdout


def test_manifest_claims_without_evidence_are_blocked(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9003-fixture"
    change_dir.mkdir(parents=True)
    manifest = _manifest()
    manifest["change"]["id"] = "CHG-9003"
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    head = _commit(tmp_path, "manifest-only complete claim")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert result.exit_code == 1
    assert "MR-016" in result.stdout


def test_ambiguous_unclassified_diff_is_blocked(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    (tmp_path / "unclassified.data").write_text("materially ambiguous\n", encoding="utf-8")
    head = _commit(tmp_path, "ambiguous change")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert result.exit_code == 1
    assert "MR-017" in result.stdout


def test_merge_check_scopes_review_subject_staleness_to_the_changes_own_directory(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    base = _commit(tmp_path, "base")

    def _freeze_change(change_id: str) -> None:
        change_dir = tmp_path / ".forge" / "changes" / f"{change_id}-fixture"
        change_dir.mkdir(parents=True)
        manifest = _manifest()
        manifest["change"]["id"] = change_id
        (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        (change_dir / "verification.md").write_text("## Result\n\n**PASS**\n", encoding="utf-8")
        (change_dir / "review.md").write_text("## Verdict\n\n**PASS**\n", encoding="utf-8")
        subject = _commit(tmp_path, f"freeze {change_id} subject")
        provenance = {"schema": "forge/execution-provenance@2", "change": change_id, "records": [
            {"id": "impl-001", "role": "implementation", "execution": {"id": "impl", "context_id": "impl-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "implementation-subject", "statement": "Fixture implementation subject."}},
            {"id": "review-001", "role": "review", "execution": {"id": "review", "context_id": "review-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "strict-review", "statement": "Fixture independent review."}},
            {"id": "verification-001", "role": "implementation", "execution": {"id": "verification", "context_id": "verification-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "verification.md", "statement": "Fixture verification evidence."}},
        ]}
        (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
        _commit(tmp_path, f"record {change_id} review-control metadata")

    # CHG-9001 is frozen and reviewed first.
    _freeze_change("CHG-9001")
    # CHG-9002 is a wholly separate Change, frozen and reviewed afterwards —
    # its commits only ever touch its own directory, never CHG-9001's.
    _freeze_change("CHG-9002")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, check=True, capture_output=True, text=True
    ).stdout.strip()

    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])

    assert "MR-015" not in result.stdout, result.stdout
    assert "MR-006" not in result.stdout, result.stdout
    assert result.exit_code == 0, result.stdout
    assert "MERGE READY" in result.stdout


def test_merge_check_flags_missing_required_stage_artifact(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9004-fixture"
    change_dir.mkdir(parents=True)
    manifest = _manifest(status="plan")
    manifest["change"]["id"] = "CHG-9004"
    manifest["review"]["iterations"] = []
    # The canonical STANDARD Flow requires a "specification" stage; this
    # manifest never declares that artifact at all. review.status stays
    # "passed" with zero blockers/majors so the unrelated
    # blocking_review_threads_resolved check does not also fire MR-009,
    # isolating this assertion to the required-stage-artifact check.
    manifest["artifacts"] = {"intent": "complete", "discovery": "complete", "plan": "complete"}
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    head = _commit(tmp_path, "record Change missing a required Flow stage artifact")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert result.exit_code == 1, result.stdout
    assert "Required artifact is missing: specification" in result.stdout, result.stdout


def _freeze_change_with_state(tmp_path, change_id: str, status: str) -> str:
    """CHG-0046: freeze a Change's Review subject with a chosen manifest
    state.current, mirroring _freeze_change's provenance shape but letting
    the caller control whether the Change has reached "complete" yet.
    Callers must write .forge/forge.yml and .forge/flows/standard.yml into
    the base commit themselves (before calling this), so those project-
    configuration files never appear in the base..head diff under test."""
    change_dir = tmp_path / ".forge" / "changes" / f"{change_id}-fixture"
    change_dir.mkdir(parents=True)
    manifest = _manifest(status=status)
    manifest["change"]["id"] = change_id
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (change_dir / "verification.md").write_text("## Result\n\n**PASS**\n", encoding="utf-8")
    (change_dir / "review.md").write_text("## Verdict\n\n**PASS**\n", encoding="utf-8")
    subject = _commit(tmp_path, f"freeze {change_id} subject ({status})")
    provenance = {"schema": "forge/execution-provenance@2", "change": change_id, "records": [
        {"id": "impl-001", "role": "implementation", "execution": {"id": "impl", "context_id": "impl-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "implementation-subject", "statement": "Fixture implementation subject."}},
        {"id": "review-001", "role": "review", "execution": {"id": "review", "context_id": "review-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "strict-review", "statement": "Fixture independent review."}},
        {"id": "verification-001", "role": "implementation", "execution": {"id": "verification", "context_id": "verification-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "verification.md", "statement": "Fixture verification evidence."}},
    ]}
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    _commit(tmp_path, f"record {change_id} review-control metadata")
    return subject


def test_merge_check_tolerates_change_local_artifact_with_anchored_renewal_record(tmp_path, monkeypatch) -> None:
    """TDD-001 / AC-001: a Change-local artifact (e.g. knowledge-capture.md,
    written by the knowledge_capture Flow stage, which every canonical Flow
    schedules after strict_review) committed after the frozen subject must
    not trip MR-015 when an explicit, anchored `role: implementation`
    provenance record exists whose commit is an ancestor of head_revision
    and whose declared `scope` covers that exact path (Protocol 2 Sec 5:
    "Appending a new provenance record... remains allowed"). This is
    CHG-0045/PR-#36's exact false-positive, resolved the Protocol-conformant
    way (Specification Drift) rather than via a `state.current` flag."""
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    _freeze_change_with_state(tmp_path, "CHG-9005", status="complete")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9005-fixture"
    (change_dir / "knowledge-capture.md").write_text("# lessons\n", encoding="utf-8")
    renewed_commit = _commit(tmp_path, "record post-Review Knowledge Capture artifact")
    provenance = yaml.safe_load((change_dir / "provenance.yml").read_text(encoding="utf-8"))
    provenance["records"].append({
        "id": "renewal-001", "role": "implementation",
        "execution": {"id": "impl-2", "context_id": "impl-context-2"},
        "revision": {"id": "fixture-renewal", "immutable_ref": {"type": "git_commit", "value": renewed_commit}, "commit": renewed_commit},
        "scope": [f".forge/changes/CHG-9005-fixture/knowledge-capture.md"],
        "source": {"assurance": "recorded", "observed_by": "self", "reference": "knowledge-capture.md", "statement": "Fixture renewal for Knowledge Capture."},
    })
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    head = _commit(tmp_path, "record renewal provenance")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert "MR-015" not in result.stdout, result.stdout
    assert result.exit_code == 0, result.stdout
    assert "MERGE READY" in result.stdout


def test_merge_check_still_flags_change_local_edit_without_renewal_record(tmp_path, monkeypatch) -> None:
    """TDD-002 / AC-003: the same kind of Change-local edit as the test
    above must still trip MR-015 when no renewal record exists at all —
    tolerance requires an explicit, anchored record; it is never granted by
    manifest state alone, at any point in the Change's lifecycle."""
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    _freeze_change_with_state(tmp_path, "CHG-9006", status="complete")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9006-fixture"
    (change_dir / "knowledge-capture.md").write_text("# lessons\n", encoding="utf-8")
    head = _commit(tmp_path, "record Change-local edit with no renewal record")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert "MR-015" in result.stdout, result.stdout
    assert result.exit_code == 1


def test_merge_check_ignores_unanchored_renewal_record(tmp_path, monkeypatch) -> None:
    """AC-006: a renewal record that is not itself anchored (its committed
    representation was later rewritten) provides no tolerance, mirroring
    MR-021's existing anchoring requirement for subject records."""
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    _freeze_change_with_state(tmp_path, "CHG-9009", status="complete")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9009-fixture"
    (change_dir / "knowledge-capture.md").write_text("# lessons\n", encoding="utf-8")
    renewed_commit = _commit(tmp_path, "record post-Review Knowledge Capture artifact")
    provenance = yaml.safe_load((change_dir / "provenance.yml").read_text(encoding="utf-8"))
    provenance["records"].append({
        "id": "renewal-001", "role": "implementation",
        "execution": {"id": "impl-2", "context_id": "impl-context-2"},
        "revision": {"id": "fixture-renewal", "immutable_ref": {"type": "git_commit", "value": renewed_commit}, "commit": renewed_commit},
        "scope": [".forge/changes/CHG-9009-fixture/knowledge-capture.md"],
        "source": {"assurance": "recorded", "observed_by": "self", "reference": "knowledge-capture.md", "statement": "Fixture renewal."},
    })
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    _commit(tmp_path, "record renewal provenance")
    # Rewrite the same renewal-001 record's content in a later commit --
    # its first committed representation no longer matches the current one.
    provenance["records"][-1]["scope"] = [".forge/changes/CHG-9009-fixture/knowledge-capture.md", ".forge/changes/CHG-9009-fixture/tasks.md"]
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    head = _commit(tmp_path, "rewrite renewal-001's scope after the fact")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert "MR-015" in result.stdout, result.stdout
    assert result.exit_code == 1


def test_merge_check_scopes_renewal_tolerance_to_the_declared_paths(tmp_path, monkeypatch) -> None:
    """AC-007: a renewal record's tolerance is scoped to exactly the paths
    it names, not the Change's entire uncovered delta in the same commit."""
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    _freeze_change_with_state(tmp_path, "CHG-9010", status="complete")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9010-fixture"
    (change_dir / "knowledge-capture.md").write_text("# lessons\n", encoding="utf-8")
    (change_dir / "specification.md").write_text("# rewritten post-freeze, not in the renewal's scope\n", encoding="utf-8")
    renewed_commit = _commit(tmp_path, "knowledge-capture.md and an unrelated specification.md rewrite")
    provenance = yaml.safe_load((change_dir / "provenance.yml").read_text(encoding="utf-8"))
    provenance["records"].append({
        "id": "renewal-001", "role": "implementation",
        "execution": {"id": "impl-2", "context_id": "impl-context-2"},
        "revision": {"id": "fixture-renewal", "immutable_ref": {"type": "git_commit", "value": renewed_commit}, "commit": renewed_commit},
        "scope": [".forge/changes/CHG-9010-fixture/knowledge-capture.md"],
        "source": {"assurance": "recorded", "observed_by": "self", "reference": "knowledge-capture.md", "statement": "Fixture renewal, scoped to knowledge-capture.md only."},
    })
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    head = _commit(tmp_path, "record renewal provenance")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert "MR-015" in result.stdout, result.stdout
    assert result.exit_code == 1


def test_merge_check_rejects_a_renewal_record_anchored_before_the_current_freeze(tmp_path, monkeypatch) -> None:
    """Resolution of Review R005 (Iteration 4, BLOCKER): a renewal record
    anchored during an EARLIER freeze cycle must not silently tolerate
    tampering introduced after a LATER freeze. The ancestor check on a
    renewal's commit needs a lower bound (subject_commit must itself be an
    ancestor of the renewal commit), not just an upper bound (the renewal
    commit must be an ancestor of head_revision) -- otherwise a renewal
    anchored once, early, would cover every subsequent freeze forever."""
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    base = _commit(tmp_path, "base")

    # First freeze/Review cycle (S1), then an old renewal record R1 bound to
    # a commit shortly after S1, scoped to knowledge-capture.md.
    subject_1 = _freeze_change_with_state(tmp_path, "CHG-9011", status="complete")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9011-fixture"
    (change_dir / "knowledge-capture.md").write_text("# lessons v1\n", encoding="utf-8")
    renewal_commit = _commit(tmp_path, "first legitimate Knowledge Capture write")
    provenance = yaml.safe_load((change_dir / "provenance.yml").read_text(encoding="utf-8"))
    provenance["records"].append({
        "id": "renewal-001", "role": "implementation",
        "execution": {"id": "impl-2", "context_id": "impl-context-2"},
        "revision": {"id": "fixture-renewal", "immutable_ref": {"type": "git_commit", "value": renewal_commit}, "commit": renewal_commit},
        "scope": [".forge/changes/CHG-9011-fixture/knowledge-capture.md"],
        "source": {"assurance": "recorded", "observed_by": "self", "reference": "knowledge-capture.md", "statement": "First legitimate renewal."},
    })
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    _commit(tmp_path, "record first renewal provenance")

    # Second freeze/Review cycle (S2): a Resolution fixes something in the
    # implementation, gets its own passed Review Iteration, becoming the
    # new final subject. Everything up to and including S2 is legitimate.
    manifest = yaml.safe_load((change_dir / "manifest.yml").read_text(encoding="utf-8"))
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "runtime.py").write_text("value = 2  # resolution fix\n", encoding="utf-8")
    subject_2 = _commit(tmp_path, "Resolution: fix runtime.py")
    provenance["records"].append({
        "id": "resolution-002", "role": "resolution",
        "execution": {"id": "impl-3", "context_id": "impl-context-3"},
        "revision": {"id": "fixture-resolution-2", "immutable_ref": {"type": "git_commit", "value": subject_2}, "commit": subject_2},
        "scope": ["src/runtime.py"], "targets": ["R-FIXTURE"],
        "source": {"assurance": "recorded", "observed_by": "self", "reference": "review.md", "statement": "Second Resolution, its own frozen subject."},
    })
    provenance["records"].append({
        "id": "review-002", "role": "review",
        "execution": {"id": "review-2", "context_id": "review-context-2"},
        "revision": {"id": "fixture-resolution-2", "immutable_ref": {"type": "git_commit", "value": subject_2}, "commit": subject_2},
        "source": {"assurance": "recorded", "observed_by": "self", "reference": "strict-review", "statement": "Second independent Review, passed."},
    })
    manifest["review"]["iterations"].append({
        "id": "review-002", "revision": "fixture-resolution-2", "status": "passed",
        "subject_provenance": "resolution-002", "reviewer_provenance": "review-002", "kind": "resolution_verification",
        "full_review_required": False, "new_material_findings": 0, "finding_classes": [],
    })
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    _commit(tmp_path, "record second freeze's review-control metadata")

    # After S2, knowledge-capture.md is touched AGAIN, with no fresh
    # renewal record -- only the stale renewal-001 (bound to a commit
    # before S2) exists.
    (change_dir / "knowledge-capture.md").write_text("# lessons v2 -- unexplained post-S2 edit\n", encoding="utf-8")
    head = _commit(tmp_path, "unexplained edit after the second freeze, no new renewal")

    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert "MR-015" in result.stdout, result.stdout
    assert result.exit_code == 1


def test_merge_check_does_not_detect_external_drift_after_completion(tmp_path, monkeypatch) -> None:
    """TDD-003 / AC-002 (characterization, not a behavior change): MR-015's
    `git diff` is scoped to `-- change_root` (evaluator.py), so it never
    inspects paths outside the Change's own directory, independent of
    state.current and independent of this Change. This test documents that
    pre-existing, Out-of-Scope gap (Discovery, Specification Out of Scope)
    so a future change to this scoping is a deliberate, visible decision,
    not a silent regression or a silent, accidental fix."""
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    (tmp_path / ".forge").mkdir()
    (tmp_path / ".forge" / "forge.yml").write_text("schema: forge/project@1\nproject:\n  name: fixture\nforge:\n  protocol: 2\nflows:\n  default: standard\n  allow_fast: true\n  auto_escalation: true\ntesting:\n  approach: tdd_first\nreview:\n  strict: true\ndocumentation:\n  impact_evaluation: required\n", encoding="utf-8")
    (tmp_path / ".forge" / "flows").mkdir()
    (tmp_path / ".forge" / "flows" / "standard.yml").write_text("schema: forge/project-flow@1\nflow:\n  canonical: standard\n  enabled: true\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "probe.py").write_text("value = 1\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    _freeze_change_with_state(tmp_path, "CHG-9007", status="complete")
    (tmp_path / "src" / "probe.py").write_text("value = 2  # changed after freeze\n", encoding="utf-8")
    head = _commit(tmp_path, "post-freeze implementation drift outside change_root")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert "MR-015" not in result.stdout, result.stdout
    assert result.exit_code == 0, result.stdout
    assert "MERGE READY" in result.stdout


def test_merge_check_degrades_gracefully_on_malformed_state_field(tmp_path, monkeypatch) -> None:
    """Resolution of Review R001: a malformed `state:` field (a bare string
    instead of a mapping) must not crash the CLI with an unhandled
    AttributeError when MR-015's is_complete check reads it — it must
    reuse the same isinstance-guarded read every other manifest-section
    access in _check_change() already uses, and degrade to a controlled
    diagnostic instead.

    Deliberately does not write .forge/forge.yml: with it present,
    evaluate_merge_readiness() runs validate_project() first, which hits an
    unrelated, pre-existing, unguarded `st=m.get("state")or{}` read at
    validation/__init__.py:321/375 (confirmed by direct reproduction, out
    of scope for CHG-0046 -- flagged separately) before _check_change() is
    ever reached, masking whether *this* Change's own evaluator.py read is
    guarded. Omitting forge.yml isolates the assertion to evaluator.py's
    own code path, which is what R001 and this Change's Scope are about."""
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9008-fixture"
    change_dir.mkdir(parents=True)
    manifest = _manifest(status="complete")
    manifest["state"] = "complete"  # malformed: bare string, not {current: ...}
    manifest["change"]["id"] = "CHG-9008"
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (change_dir / "verification.md").write_text("## Result\n\n**PASS**\n", encoding="utf-8")
    (change_dir / "review.md").write_text("## Verdict\n\n**PASS**\n", encoding="utf-8")
    subject = _commit(tmp_path, "freeze CHG-9008 subject with malformed state")
    provenance = {"schema": "forge/execution-provenance@2", "change": "CHG-9008", "records": [
        {"id": "impl-001", "role": "implementation", "execution": {"id": "impl", "context_id": "impl-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "implementation-subject", "statement": "Fixture."}},
        {"id": "review-001", "role": "review", "execution": {"id": "review", "context_id": "review-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "strict-review", "statement": "Fixture."}},
        {"id": "verification-001", "role": "implementation", "execution": {"id": "verification", "context_id": "verification-context"}, "revision": {"id": "fixture", "immutable_ref": {"type": "git_commit", "value": subject}, "commit": subject}, "source": {"assurance": "recorded", "observed_by": "self", "reference": "verification.md", "statement": "Fixture."}},
    ]}
    (change_dir / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")
    head = _commit(tmp_path, "record review-control metadata")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert result.exception is None or isinstance(result.exception, SystemExit), (
        f"unhandled exception (not a controlled CLI exit): {result.exception!r}"
    )
    assert "MERGE BLOCKED" in result.stdout or "MERGE READY" in result.stdout, result.stdout


def test_merge_check_blocks_stale_plan_digest(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("base\n", encoding="utf-8")
    base = _commit(tmp_path, "base")
    change_dir = tmp_path / ".forge" / "changes" / "CHG-9002-fixture"
    change_dir.mkdir(parents=True)
    manifest = _manifest()
    manifest["change"]["id"] = "CHG-9002"
    manifest["artifacts"] = {"plan": "approved"}
    (change_dir / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (change_dir / "plan.md").write_text("# approved plan\n", encoding="utf-8")
    (change_dir / "provenance.yml").write_text(
        yaml.safe_dump({"records": [{"source": {"reference": "plan.md#approval-record", "content_digest": {"value": "0" * 64}}}]}, sort_keys=False),
        encoding="utf-8",
    )
    head = _commit(tmp_path, "record stale Plan")
    result = runner.invoke(app, ["change", "merge-check", "--base", base, "--head", head])
    assert result.exit_code == 1
    assert "MR-008" in result.stdout
