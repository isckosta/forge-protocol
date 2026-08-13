from pathlib import Path

from forge_cli import validation


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_ROOT = REPOSITORY_ROOT / "protocol"


def _write_valid_project_configuration(project_root: Path) -> None:
    forge_dir = project_root / ".forge"
    forge_dir.mkdir(parents=True)
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


def test_valid_project_returns_passed_result(tmp_path: Path) -> None:
    _write_valid_project_configuration(tmp_path)

    result = validation.validate_project(tmp_path, PROTOCOL_ROOT)

    assert result.passed is True
    assert result.findings == ()


def test_missing_workspace_returns_actionable_not_initialized_finding(tmp_path: Path) -> None:
    result = validation.validate_project(tmp_path, PROTOCOL_ROOT)

    assert result.passed is False
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.code == "E_FORGE_NOT_INITIALIZED"
    assert finding.artifact == ".forge/"
    assert finding.path == tmp_path / ".forge"
    assert "forge init" in finding.message


def test_unknown_project_flow_returns_actionable_finding(tmp_path: Path) -> None:
    _write_valid_project_configuration(tmp_path)
    flow_dir = tmp_path / ".forge" / "flows"
    flow_dir.mkdir()
    (flow_dir / "custom.yml").write_text(
        "schema: forge/project-flow@1\n"
        "flow:\n"
        "  canonical: imaginary\n"
        "  enabled: true\n",
        encoding="utf-8",
    )

    result = validation.validate_project(tmp_path, PROTOCOL_ROOT)

    assert result.passed is False
    assert result.findings[0].code == "E_FORGE_UNKNOWN_CANONICAL_FLOW"
    assert result.findings[0].artifact == ".forge/flows/custom.yml"


def test_missing_canonical_contract_returns_actionable_finding(tmp_path: Path) -> None:
    _write_valid_project_configuration(tmp_path)
    protocol_root = tmp_path / "protocol"
    (protocol_root / "flows").mkdir(parents=True)

    result = validation.validate_project(tmp_path, protocol_root)

    assert result.passed is False
    assert result.findings[0].code == "E_FORGE_CANONICAL_CONTRACT_UNAVAILABLE"
    assert result.findings[0].artifact == "protocol/contract/engineering.md"
