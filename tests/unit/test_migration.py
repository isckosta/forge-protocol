from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_CANDIDATE_CHANGE_IDS = (
    "CHG-0008-reviewer-resolver-separation",
    "CHG-0011-review-convergence-boundary",
    "CHG-0012-freeze-check-exempts-complete-changes",
    "CHG-0013-unresolved-decision-management",
    "CHG-0014-golden-path-codex-onboarding",
    "CHG-0015-delegated-agent-authority-and-side-effect-boundaries",
)


def _write_provenance(path: Path, *, schema: str, roles: list[str]) -> None:
    records = "\n".join(
        f"  - id: r{i}\n    role: {role}\n    execution: {{id: e{i}, context_id: c{i}}}\n"
        for i, role in enumerate(roles)
    )
    path.write_text(f"schema: {schema}\nchange: CHG-TEST\nrecords:\n{records}", encoding="utf-8")


def _make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    (project / ".forge" / "changes").mkdir(parents=True)
    return project


def test_finds_execution_provenance_v1_candidate_without_delegated_task(tmp_path: Path) -> None:
    from forge_cli.migration import find_candidates

    project = _make_project(tmp_path)
    change_dir = project / ".forge" / "changes" / "CHG-0001-example"
    change_dir.mkdir()
    _write_provenance(
        change_dir / "provenance.yml",
        schema="forge/execution-provenance@1",
        roles=["implementation", "review"],
    )

    candidates = find_candidates(project)

    assert len(candidates) == 1
    assert candidates[0].change_id == "CHG-0001-example"
    assert candidates[0].path == change_dir / "provenance.yml"


def test_ignores_provenance_already_on_v2(tmp_path: Path) -> None:
    from forge_cli.migration import find_candidates

    project = _make_project(tmp_path)
    change_dir = project / ".forge" / "changes" / "CHG-0002-example"
    change_dir.mkdir()
    _write_provenance(
        change_dir / "provenance.yml",
        schema="forge/execution-provenance@2",
        roles=["implementation"],
    )

    assert find_candidates(project) == ()


def test_refuses_provenance_containing_a_delegated_task_record(tmp_path: Path) -> None:
    """FR-003/NFR-001: never touch a record this Change cannot prove is
    a safe superset for."""
    from forge_cli.migration import find_candidates

    project = _make_project(tmp_path)
    change_dir = project / ".forge" / "changes" / "CHG-0003-example"
    change_dir.mkdir()
    _write_provenance(
        change_dir / "provenance.yml",
        schema="forge/execution-provenance@1",
        roles=["implementation", "delegated_task"],
    )

    assert find_candidates(project) == ()


def test_ignores_missing_changes_directory(tmp_path: Path) -> None:
    from forge_cli.migration import find_candidates

    project = tmp_path / "empty-project"
    project.mkdir()

    assert find_candidates(project) == ()


def test_apply_migrations_rewrites_only_the_schema_line(tmp_path: Path) -> None:
    from forge_cli.migration import apply_migrations, find_candidates

    project = _make_project(tmp_path)
    change_dir = project / ".forge" / "changes" / "CHG-0004-example"
    change_dir.mkdir()
    path = change_dir / "provenance.yml"
    original = (
        "schema: forge/execution-provenance@1\n"
        "change: CHG-0004\n"
        "records:\n"
        "  - id: implementation-001\n"
        "    role: implementation\n"
        "    execution: {id: e1, context_id: c1}\n"
    )
    path.write_text(original, encoding="utf-8")

    candidates = find_candidates(project)
    results = apply_migrations(project, candidates)

    assert len(results) == 1
    rewritten = path.read_text(encoding="utf-8")
    expected = original.replace(
        "forge/execution-provenance@1", "forge/execution-provenance@2"
    )
    assert rewritten == expected
    # Only the schema line differs -- every other line is byte-identical.
    original_lines = original.splitlines()
    rewritten_lines = rewritten.splitlines()
    differing = [
        i for i, (a, b) in enumerate(zip(original_lines, rewritten_lines)) if a != b
    ]
    assert differing == [0]


def test_apply_migrations_is_idempotent(tmp_path: Path) -> None:
    from forge_cli.migration import apply_migrations, find_candidates

    project = _make_project(tmp_path)
    change_dir = project / ".forge" / "changes" / "CHG-0005-example"
    change_dir.mkdir()
    _write_provenance(
        change_dir / "provenance.yml",
        schema="forge/execution-provenance@1",
        roles=["implementation"],
    )

    apply_migrations(project, find_candidates(project))
    second_run_candidates = find_candidates(project)
    second_run_results = apply_migrations(project, second_run_candidates)

    assert second_run_candidates == ()
    assert second_run_results == ()


def test_never_scans_change_or_adapter_installation_files(tmp_path: Path) -> None:
    """FR-003: this Change's forge migrate recognizes exactly one schema
    family -- forge/change@1 is explicitly forbidden from migration by
    compatibility.md, and adapter-installation needs non-derivable input."""
    from forge_cli.migration import find_candidates

    project = _make_project(tmp_path)
    change_dir = project / ".forge" / "changes" / "CHG-0006-example"
    change_dir.mkdir()
    (change_dir / "manifest.yml").write_text(
        "schema: forge/change@1\nchange: {id: CHG-0006}\n", encoding="utf-8"
    )

    assert find_candidates(project) == ()


def test_real_historical_provenance_fixtures_yield_exactly_six_candidates(tmp_path: Path) -> None:
    """CON-004: copies this repository's own real historical provenance
    files into a disposable fixture -- never reads or writes the
    originals under .forge/changes/ directly."""
    from forge_cli.migration import apply_migrations, find_candidates

    project = _make_project(tmp_path)
    real_changes_dir = REPO_ROOT / ".forge" / "changes"
    for change_id in REAL_CANDIDATE_CHANGE_IDS:
        source = real_changes_dir / change_id / "provenance.yml"
        destination_dir = project / ".forge" / "changes" / change_id
        destination_dir.mkdir(parents=True)
        shutil.copyfile(source, destination_dir / "provenance.yml")

    candidates = find_candidates(project)
    assert {candidate.change_id for candidate in candidates} == set(REAL_CANDIDATE_CHANGE_IDS)

    results = apply_migrations(project, candidates)
    assert len(results) == 6
    for change_id in REAL_CANDIDATE_CHANGE_IDS:
        migrated_path = project / ".forge" / "changes" / change_id / "provenance.yml"
        original_path = real_changes_dir / change_id / "provenance.yml"
        migrated_lines = migrated_path.read_text(encoding="utf-8").splitlines()
        original_lines = original_path.read_text(encoding="utf-8").splitlines()
        assert migrated_lines[0] == "schema: forge/execution-provenance@2"
        assert original_lines[0] == "schema: forge/execution-provenance@1"
        assert migrated_lines[1:] == original_lines[1:]

    # The real, original files under .forge/changes/ are untouched.
    for change_id in REAL_CANDIDATE_CHANGE_IDS:
        assert (real_changes_dir / change_id / "provenance.yml").read_text(
            encoding="utf-8"
        ).splitlines()[0] == "schema: forge/execution-provenance@1"
