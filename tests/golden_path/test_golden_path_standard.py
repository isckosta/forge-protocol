"""Golden Path (STANDARD, Codex) — Layer A and Layer B deterministic evidence.

Layer A proves the CLI/Adapter readiness sequence (`forge init` -> `forge
adapter install codex` -> `forge doctor`) added/extended by CHG-0014.

Layer B proves that a real STANDARD Change, built with genuine chronological
TDD against the `examples/golden-path-standard/starter/` fixture, produces
repository-native artifacts that validate through `forge validate` and
directly against the canonical JSON Schema — not merely through a
hand-rolled parallel checker.

Neither test asserts on Codex's own behavior (Layer C); see
`examples/golden-path-standard/README.md` for that manual procedure.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

from jsonschema import Draft202012Validator
from typer.testing import CliRunner
import yaml

from forge_cli.app import app
from forge_cli.validation import validate_project


REPO_ROOT = Path(__file__).resolve().parents[2]
STARTER_FIXTURE = REPO_ROOT / "examples" / "golden-path-standard" / "starter"
PROTOCOL_ROOT = REPO_ROOT / "protocol"
CHANGE_SCHEMA_PATH = PROTOCOL_ROOT / "schemas" / "change-v2.schema.json"
TDD_EVIDENCE_SCHEMA_PATH = PROTOCOL_ROOT / "schemas" / "tdd-evidence.schema.json"

runner = CliRunner()


def _git(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=check, capture_output=True, text=True
    )


def _commit_all(cwd: Path, message: str) -> str:
    _git("add", "-A", cwd=cwd)
    _git("commit", "-q", "-m", message, cwd=cwd)
    return _git("rev-parse", "HEAD", cwd=cwd).stdout.strip()


def _run_pytest(cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def _init_fixture_git_identity(cwd: Path) -> None:
    _git("init", "-q", cwd=cwd)
    _git("config", "user.email", "golden-path@example.invalid", cwd=cwd)
    _git("config", "user.name", "Golden Path Fixture", cwd=cwd)


def test_readiness_sequence_surfaces_adapter_install_and_health(
    tmp_path: Path, monkeypatch
) -> None:
    """Layer A: forge init -> adapter install codex -> forge doctor, end to end."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git("init", "-q", cwd=repo)
    monkeypatch.chdir(repo)

    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0, init_result.output

    doctor_before_adapter = runner.invoke(app, ["doctor"])
    assert doctor_before_adapter.exit_code == 0, doctor_before_adapter.output
    assert "adapter:codex:" not in doctor_before_adapter.stdout

    install_result = runner.invoke(app, ["adapter", "install", "codex"])
    assert install_result.exit_code == 0, install_result.output
    assert "codex Adapter installed at .agents/skills/forge." in install_result.stdout
    assert "Open codex in this repository" in install_result.stdout

    healthy_doctor = runner.invoke(app, ["doctor"])
    assert healthy_doctor.exit_code == 0, healthy_doctor.output
    assert "PASS adapter:codex:generated_drift" in healthy_doctor.stdout
    assert "PASS adapter:codex:conformance" in healthy_doctor.stdout

    skill = repo / ".agents" / "skills" / "forge" / "SKILL.md"
    assert "Implementation MUST NOT begin until" in skill.read_text(encoding="utf-8")
    skill.write_bytes(skill.read_bytes() + b"\n# deliberate drift for this test\n")

    drifted_doctor = runner.invoke(app, ["doctor"])
    assert drifted_doctor.exit_code == 2
    assert "FAIL adapter:codex:generated_drift" in drifted_doctor.stdout


def test_golden_path_produces_a_valid_standard_change(
    tmp_path: Path, monkeypatch
) -> None:
    """Layer B: a real, chronological TDD cycle against the fixture, then
    repository-native Change artifacts that validate mechanically."""
    fixture = tmp_path / "fixture"
    shutil.copytree(STARTER_FIXTURE, fixture)
    _init_fixture_git_identity(fixture)
    _commit_all(fixture, "baseline: create_username with no length rule")

    baseline_run = _run_pytest(fixture)
    assert baseline_run.returncode == 0, baseline_run.stdout + baseline_run.stderr

    monkeypatch.chdir(fixture)
    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0, init_result.output

    change_dir = fixture / ".forge" / "changes" / "CHG-0001-username-length-validation"
    change_dir.mkdir(parents=True)
    (change_dir / "intent.md").write_text(
        "# Intent\n\n"
        "Reject usernames shorter than three characters in `create_username`.\n"
        "Currently only emptiness is rejected.\n",
        encoding="utf-8",
    )
    (change_dir / "discovery.md").write_text(
        "# Discovery\n\nSingle function, `src/accounts/users.py::create_username`. "
        "No other caller depends on short names being accepted "
        "(`tests/test_users.py` is the only caller in this fixture).\n",
        encoding="utf-8",
    )
    (change_dir / "specification.md").write_text(
        "# Specification\n\n"
        "FR-001: `create_username` MUST raise `ValueError` for names shorter than "
        "three characters, in addition to the existing empty-name rule.\n",
        encoding="utf-8",
    )
    (change_dir / "plan.md").write_text(
        "# Plan\n\nAdd a length check to `create_username`. TDD: write a failing "
        "test for a two-character name first, observe it fail, then implement "
        "the minimal check.\n\n**Plan ready. Implementation follows this commit.**\n",
        encoding="utf-8",
    )
    (change_dir / "test-design.md").write_text(
        "# Test Design\n\n`test_create_username_rejects_short_names` asserts "
        "`create_username(\"ab\")` raises `ValueError`.\n",
        encoding="utf-8",
    )
    planning_commit = _commit_all(
        fixture, "plan: CHG-0001 intent, discovery, specification, plan, test design"
    )

    # RED: the test is written and run before any production-code change.
    test_file = fixture / "tests" / "test_users.py"
    red_test_source = test_file.read_text(encoding="utf-8") + (
        "\n\n"
        "def test_create_username_rejects_short_names() -> None:\n"
        "    with pytest.raises(ValueError):\n"
        "        create_username(\"ab\")\n"
    )
    test_file.write_text(red_test_source, encoding="utf-8")
    red_run = _run_pytest(fixture)
    assert red_run.returncode != 0, (
        "expected genuine RED before the fix exists:\n" + red_run.stdout
    )
    assert "test_create_username_rejects_short_names" in red_run.stdout
    assert "DID NOT RAISE" in red_run.stdout
    red_commit = _commit_all(fixture, "red: failing test for short-username rejection")

    # GREEN: minimal production fix, run again to confirm.
    source_file = fixture / "src" / "accounts" / "users.py"
    source_file.write_text(
        "def create_username(name: str) -> str:\n"
        "    if not name:\n"
        "        raise ValueError(\"username must not be empty\")\n"
        "    if len(name) < 3:\n"
        "        raise ValueError(\"username must be at least three characters\")\n"
        "    return name\n",
        encoding="utf-8",
    )
    green_run = _run_pytest(fixture)
    assert green_run.returncode == 0, green_run.stdout + green_run.stderr
    assert "3 passed" in green_run.stdout

    manifest = {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {
            "id": "CHG-0001",
            "title": "Reject usernames shorter than three characters",
            "kind": "feature",
        },
        "flow": {"initial": "standard", "current": "standard", "escalations": []},
        "state": {"current": "verification"},
        "artifacts": {
            "intent": "complete",
            "discovery": "complete",
            "specification": "complete",
            "plan": "complete",
            "test_design": "complete",
            "tdd_evidence": "complete",
            "implementation": "complete",
            "verification": "complete",
            "review": "pending",
            "documentation": "complete",
        },
        "requirements": {"total": 1, "implemented": 1, "verified": 1},
        "tdd": {"status": "compliant", "cycles": 1},
        "verification": {"status": "passed"},
        "review": {
            "status": "pending",
            "iteration": 0,
            "blockers": 0,
            "majors": 0,
            "minors": 0,
            "observations": 0,
            "iterations": [],
        },
        "documentation": {
            "impact_evaluated": True,
            "update_required": False,
            "reason": (
                "Behavioral rule change with no external documentation surface "
                "in this fixture."
            ),
        },
    }
    (change_dir / "manifest.yml").write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    red_failure_line = next(
        line for line in red_run.stdout.splitlines() if "DID NOT RAISE" in line
    ).strip()
    tdd_evidence = {
        "schema": "forge/tdd-evidence@1",
        "change": "CHG-0001",
        "status": "compliant",
        "cycle_count": 1,
        "cycles": [
            {
                "id": "TDD-001",
                "title": "Reject usernames shorter than three characters",
                "requirements": ["FR-001"],
                "red": {
                    "observed": True,
                    "failure_reason": (
                        "test_create_username_rejects_short_names failed before the "
                        f"length check existed: {red_failure_line}"
                    ),
                },
                "green": {
                    "observed": True,
                    "evidence": (
                        "Full suite passes after adding the length check "
                        f"({green_run.stdout.strip().splitlines()[-1]})"
                    ),
                },
            }
        ],
        "notes": [],
    }
    (change_dir / "tdd-evidence.yml").write_text(
        yaml.safe_dump(tdd_evidence, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (change_dir / "verification.md").write_text(
        "# Verification\n\n"
        f"`pytest -q` against the fixture: {green_run.stdout.strip().splitlines()[-1]}. "
        "No other verification surface applies to this toy fixture.\n",
        encoding="utf-8",
    )
    implementation_commit = _commit_all(
        fixture,
        "implement: reject usernames shorter than three characters (GREEN); "
        "record TDD evidence and manifest",
    )

    # Ordering (FR-008): Plan strictly precedes RED strictly precedes Implementation.
    assert (
        _git(
            "merge-base", "--is-ancestor", planning_commit, red_commit,
            cwd=fixture, check=False,
        ).returncode
        == 0
    )
    assert (
        _git(
            "merge-base", "--is-ancestor", red_commit, implementation_commit,
            cwd=fixture, check=False,
        ).returncode
        == 0
    )
    plan_files_at_red_commit = _git(
        "show", f"{red_commit}:.forge/changes/CHG-0001-username-length-validation/plan.md",
        cwd=fixture,
    ).stdout
    assert "Plan ready" in plan_files_at_red_commit
    production_diff_before_green = _git(
        "diff", "--name-only", planning_commit, red_commit, cwd=fixture
    ).stdout
    assert "src/accounts/users.py" not in production_diff_before_green.splitlines()

    # Repository outcome (FR-007): forge validate accepts the fixture Change.
    validation_result = validate_project(fixture, PROTOCOL_ROOT)
    assert validation_result.passed, validation_result.findings

    cli_validate = runner.invoke(app, ["validate"])
    assert cli_validate.exit_code == 0, cli_validate.output
    assert "Forge project is valid" in cli_validate.stdout

    # Independent schema conformance (stronger than `forge validate`, which
    # does not itself perform JSON Schema validation of manifest.yml today
    # -- see discovery.md).
    change_schema = json.loads(CHANGE_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(change_schema)
    Draft202012Validator(change_schema).validate(manifest)

    tdd_schema = json.loads(TDD_EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(tdd_schema)
    Draft202012Validator(tdd_schema).validate(tdd_evidence)

    assert manifest["flow"]["current"] == "standard"
    assert tdd_evidence["cycles"][0]["red"]["observed"] is True
    assert tdd_evidence["cycles"][0]["green"]["observed"] is True
