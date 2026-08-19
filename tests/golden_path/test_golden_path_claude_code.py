"""Golden Path (STANDARD, Claude Code) -- Layer A and Layer B deterministic
evidence.

Layer A proves the CLI/Adapter readiness sequence (`forge init` -> `forge
adapter install claude-code` -> `forge doctor`).

Layer B proves that a real STANDARD Change, built against the
`examples/golden-path-claude-code/starter/` fixture, produces
repository-native artifacts that validate through `forge validate` and
directly against the canonical JSON Schema.

Layer C -- whether a live Claude Code session actually behaves correctly
when it opens a repository with this Adapter installed -- is not
mechanically testable the way Layer A/B are (no test harness can drive a
live model session). Unlike the existing Codex Golden Path
(`examples/golden-path-standard/README.md`), which stops at Layer B
because Layer C needs a human operating a separate tool, this repository
can genuinely execute Layer C for Claude Code, because the Harness in
question is the very session producing this Change (CHG-0018) -- see
`examples/golden-path-claude-code/README.md` and this Change's own
`verification.md` for that evidence, recorded as a real, dated
transcript of an actual run, not narrated or simulated.
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
STARTER_FIXTURE = REPO_ROOT / "examples" / "golden-path-claude-code" / "starter"
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
    """Layer A: forge init -> adapter install claude-code -> forge doctor."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git("init", "-q", cwd=repo)
    monkeypatch.chdir(repo)

    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0, init_result.output

    doctor_before_adapter = runner.invoke(app, ["doctor"])
    assert doctor_before_adapter.exit_code == 0, doctor_before_adapter.output
    assert "adapter:claude-code:" not in doctor_before_adapter.stdout

    install_result = runner.invoke(app, ["adapter", "install", "claude-code"])
    assert install_result.exit_code == 0, install_result.output
    assert "claude-code Adapter installed at .claude." in install_result.stdout
    assert "Open claude-code in this repository" in install_result.stdout

    healthy_doctor = runner.invoke(app, ["doctor"])
    assert healthy_doctor.exit_code == 0, healthy_doctor.output
    assert "PASS adapter:claude-code:generated_drift" in healthy_doctor.stdout
    assert "PASS adapter:claude-code:conformance" in healthy_doctor.stdout

    skill = repo / ".claude" / "skills" / "forge" / "SKILL.md"
    assert "Implementation MUST NOT begin until" in skill.read_text(encoding="utf-8")
    claude_md = repo / ".claude" / "CLAUDE.md"
    assert "forge" in claude_md.read_text(encoding="utf-8").lower()
    hook_script = repo / ".claude" / "skills" / "forge" / "hooks" / "check-manifest-edit.sh"
    assert hook_script.is_file()

    skill.write_bytes(skill.read_bytes() + b"\n# deliberate drift for this test\n")

    drifted_doctor = runner.invoke(app, ["doctor"])
    assert drifted_doctor.exit_code == 2
    assert "FAIL adapter:claude-code:generated_drift" in drifted_doctor.stdout


def test_golden_path_produces_a_valid_standard_change(
    tmp_path: Path, monkeypatch
) -> None:
    """Layer B: a real, chronological TDD cycle against the fixture, then
    repository-native Change artifacts that validate mechanically."""
    fixture = tmp_path / "fixture"
    shutil.copytree(STARTER_FIXTURE, fixture)
    _init_fixture_git_identity(fixture)
    _commit_all(fixture, "baseline: greet with no whitespace-only rule")

    baseline_run = _run_pytest(fixture)
    assert baseline_run.returncode == 0, baseline_run.stdout + baseline_run.stderr

    monkeypatch.chdir(fixture)
    init_result = runner.invoke(app, ["init"])
    assert init_result.exit_code == 0, init_result.output

    change_dir = fixture / ".forge" / "changes" / "CHG-0001-reject-whitespace-only-name"
    change_dir.mkdir(parents=True)
    (change_dir / "intent.md").write_text(
        "# Intent\n\nReject a whitespace-only name in `greet`. Currently only "
        "the empty string is rejected; \" \" passes through and produces "
        "\"Hello,  !\".\n",
        encoding="utf-8",
    )
    (change_dir / "discovery.md").write_text(
        "# Discovery\n\nSingle function, `src/greeting/greeter.py::greet`. "
        "`tests/test_greeter.py` is the only caller in this fixture.\n",
        encoding="utf-8",
    )
    (change_dir / "specification.md").write_text(
        "# Specification\n\nFR-001: `greet` MUST raise `ValueError` for a name "
        "that is empty or contains only whitespace, in addition to the "
        "existing empty-name rule.\n",
        encoding="utf-8",
    )
    (change_dir / "plan.md").write_text(
        "# Plan\n\nAdd a whitespace-only check to `greet`. TDD: write a failing "
        "test for a whitespace-only name first, observe it fail, then "
        "implement the minimal check.\n\n**Plan ready. Implementation follows "
        "this commit.**\n",
        encoding="utf-8",
    )
    (change_dir / "test-design.md").write_text(
        "# Test Design\n\n`test_greet_rejects_whitespace_only_name` asserts "
        "`greet(\"   \")` raises `ValueError`.\n",
        encoding="utf-8",
    )
    planning_commit = _commit_all(
        fixture, "plan: CHG-0001 intent, discovery, specification, plan, test design"
    )

    # RED: the test is written and run before any production-code change.
    test_file = fixture / "tests" / "test_greeter.py"
    red_test_source = test_file.read_text(encoding="utf-8") + (
        "\n\n"
        "def test_greet_rejects_whitespace_only_name() -> None:\n"
        "    with pytest.raises(ValueError):\n"
        "        greet(\"   \")\n"
    )
    test_file.write_text(red_test_source, encoding="utf-8")
    red_run = _run_pytest(fixture)
    assert red_run.returncode != 0, (
        "expected genuine RED before the fix exists:\n" + red_run.stdout
    )
    assert "test_greet_rejects_whitespace_only_name" in red_run.stdout
    assert "DID NOT RAISE" in red_run.stdout
    red_commit = _commit_all(fixture, "red: failing test for whitespace-only name rejection")

    # GREEN: minimal production fix, run again to confirm.
    source_file = fixture / "src" / "greeting" / "greeter.py"
    source_file.write_text(
        "def greet(name: str) -> str:\n"
        "    if not name or not name.strip():\n"
        "        raise ValueError(\"name must not be empty\")\n"
        "    return f\"Hello, {name}!\"\n",
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
            "title": "Reject a whitespace-only name in greet",
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
                "title": "Reject a whitespace-only name in greet",
                "requirements": ["FR-001"],
                "red": {
                    "observed": True,
                    "failure_reason": (
                        "test_greet_rejects_whitespace_only_name failed before "
                        f"the whitespace check existed: {red_failure_line}"
                    ),
                },
                "green": {
                    "observed": True,
                    "evidence": (
                        "Full suite passes after adding the whitespace check "
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
        "implement: reject whitespace-only name (GREEN); record TDD evidence and manifest",
    )

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
        "show", f"{red_commit}:.forge/changes/CHG-0001-reject-whitespace-only-name/plan.md",
        cwd=fixture,
    ).stdout
    assert "Plan ready" in plan_files_at_red_commit
    production_diff_before_green = _git(
        "diff", "--name-only", planning_commit, red_commit, cwd=fixture
    ).stdout
    assert "src/greeting/greeter.py" not in production_diff_before_green.splitlines()

    validation_result = validate_project(fixture, PROTOCOL_ROOT)
    assert validation_result.passed, validation_result.findings

    cli_validate = runner.invoke(app, ["validate"])
    assert cli_validate.exit_code == 0, cli_validate.output
    assert "Forge project is valid" in cli_validate.stdout

    change_schema = json.loads(CHANGE_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(change_schema)
    Draft202012Validator(change_schema).validate(manifest)

    tdd_schema = json.loads(TDD_EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(tdd_schema)
    Draft202012Validator(tdd_schema).validate(tdd_evidence)

    assert manifest["flow"]["current"] == "standard"
    assert tdd_evidence["cycles"][0]["red"]["observed"] is True
    assert tdd_evidence["cycles"][0]["green"]["observed"] is True
