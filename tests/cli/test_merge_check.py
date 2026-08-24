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
