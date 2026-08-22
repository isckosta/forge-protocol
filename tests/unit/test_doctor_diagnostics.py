from pathlib import Path
import subprocess

from typer.testing import CliRunner

from forge_cli import doctor
from forge_cli.app import app


PROTOCOL_ROOT = Path(__file__).resolve().parents[2] / "protocol"
runner = CliRunner()


def _init_git_repository(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)


def _write_valid_project_configuration(project_root: Path) -> None:
    forge_dir = project_root / ".forge"
    forge_dir.mkdir()
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


def test_doctor_passes_all_required_checks_for_valid_project(tmp_path: Path) -> None:
    _init_git_repository(tmp_path)
    _write_valid_project_configuration(tmp_path)

    result = doctor.diagnose(tmp_path, PROTOCOL_ROOT)

    assert result.passed is True
    assert [check.id for check in result.checks] == [
        "git_available",
        "git_repository",
        "forge_initialized",
        "project_configuration",
        "protocol_compatibility",
        "canonical_flows",
        "canonical_contract",
    ]
    assert all(check.status == "passed" for check in result.checks)


def test_doctor_aggregates_failure_and_skipped_checks(tmp_path: Path) -> None:
    _init_git_repository(tmp_path)

    result = doctor.diagnose(tmp_path, PROTOCOL_ROOT)

    checks = {check.id: check for check in result.checks}
    assert checks["git_available"].status == "passed"
    assert checks["git_repository"].status == "passed"
    assert checks["forge_initialized"].status == "failed"
    assert checks["project_configuration"].status == "skipped"
    assert checks["protocol_compatibility"].status == "skipped"
    assert checks["canonical_flows"].status == "skipped"
    assert checks["canonical_contract"].status == "passed"
    assert result.passed is False


def test_doctor_skips_repository_dependent_checks_outside_git(tmp_path: Path) -> None:
    result = doctor.diagnose(tmp_path, PROTOCOL_ROOT)

    checks = {check.id: check for check in result.checks}
    assert checks["git_available"].status == "passed"
    assert checks["git_repository"].status == "failed"
    assert checks["forge_initialized"].status == "skipped"
    assert checks["project_configuration"].status == "skipped"
    assert checks["protocol_compatibility"].status == "skipped"
    assert checks["canonical_flows"].status == "skipped"
    assert checks["canonical_contract"].status == "passed"


def test_doctor_reports_installed_adapter_readiness(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["adapter", "install", "codex"])

    result = doctor.diagnose(tmp_path, PROTOCOL_ROOT)

    assert result.passed is True
    adapter_checks = {
        check.id: check for check in result.checks if check.id.startswith("adapter:codex:")
    }
    assert adapter_checks
    assert all(check.status != "failed" for check in adapter_checks.values())
    # The Codex Adapter has known, expected capability limitations (represented,
    # not enforced) -- a healthy install legitimately carries a "warning" status
    # check for that, which must not be relabeled "passed" (CHG-0014-R002).
    assert adapter_checks["adapter:codex:limitations"].status == "warning"
    assert adapter_checks["adapter:codex:configuration"].status == "passed"


def test_doctor_preserves_adapter_warning_status_instead_of_relabeling_as_passed(
    tmp_path: Path, monkeypatch
) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["adapter", "install", "codex"])
    (tmp_path / ".forge" / "forge.yml").write_text("not: [valid yaml", encoding="utf-8")

    result = doctor.diagnose(tmp_path, PROTOCOL_ROOT)

    compatibility = next(
        check for check in result.checks if check.id == "adapter:codex:compatibility"
    )
    assert compatibility.status == "warning"
    assert compatibility.status != "passed"
    assert "cannot be checked" in compatibility.message


def test_doctor_reports_drifted_adapter_as_failed(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    runner.invoke(app, ["adapter", "install", "codex"])
    skill = tmp_path / ".agents" / "skills" / "forge" / "SKILL.md"
    skill.write_bytes(skill.read_bytes() + b"\n# deliberate drift\n")

    result = doctor.diagnose(tmp_path, PROTOCOL_ROOT)

    assert result.passed is False
    assert any(
        check.id == "adapter:codex:generated_drift" and check.status == "failed"
        for check in result.checks
    )


def test_doctor_warns_when_no_adapter_is_installed(tmp_path: Path, monkeypatch) -> None:
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = doctor.diagnose(tmp_path, PROTOCOL_ROOT)

    adapter_checks = [check for check in result.checks if check.id.startswith("adapter:")]

    assert len(adapter_checks) == 1
    assert adapter_checks[0].status == "warning"
    assert "No Adapter is installed" in adapter_checks[0].message
    assert "forge adapter install" in adapter_checks[0].message


def test_doctor_is_read_only(tmp_path: Path) -> None:
    _init_git_repository(tmp_path)
    marker = tmp_path / "marker.txt"
    marker.write_text("unchanged", encoding="utf-8")
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*") if ".git" not in path.parts)

    doctor.diagnose(tmp_path, PROTOCOL_ROOT)

    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*") if ".git" not in path.parts)
    assert after == before
    assert marker.read_text(encoding="utf-8") == "unchanged"
