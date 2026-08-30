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


def _write_project_flow_override(project_root: Path, flow_id: str, profile: str) -> None:
    flow_dir = project_root / ".forge" / "flows"
    flow_dir.mkdir(parents=True, exist_ok=True)
    (flow_dir / f"{flow_id}.yml").write_text(
        "schema: forge/project-flow@1\n"
        "flow:\n"
        f"  canonical: {flow_id}\n"
        "  enabled: true\n"
        "review:\n"
        f"  profile: {profile}\n",
        encoding="utf-8",
    )


def test_profile_floor_rejects_a_weaker_than_canonical_project_override(tmp_path: Path) -> None:
    _write_valid_project_configuration(tmp_path)
    _write_project_flow_override(tmp_path, "full", "focused")

    result = validation.validate_project(tmp_path, PROTOCOL_ROOT)

    assert result.passed is False
    messages = [f.message for f in result.findings]
    assert any("focused" in m and "strict" in m for m in messages)


def test_profile_floor_accepts_a_stricter_than_canonical_project_override(tmp_path: Path) -> None:
    _write_valid_project_configuration(tmp_path)
    _write_project_flow_override(tmp_path, "fast", "strict")

    result = validation.validate_project(tmp_path, PROTOCOL_ROOT)

    assert result.passed is True
    assert result.findings == ()


def test_compute_review_profile_floor_returns_canonical_profile_without_override() -> None:
    effective = {
        "canonical": {"flow": {"id": "standard", "review": {"profile": "standard"}}},
        "project": {},
    }

    assert validation.compute_review_profile_floor(effective) == "standard"


def test_compute_review_profile_floor_returns_project_override_profile() -> None:
    effective = {
        "canonical": {"flow": {"id": "fast", "review": {"profile": "focused"}}},
        "project": {"review": {"profile": "strict"}},
    }

    assert validation.compute_review_profile_floor(effective) == "strict"


def test_profile_floor_is_silent_when_project_declares_no_profile_override(tmp_path: Path) -> None:
    _write_valid_project_configuration(tmp_path)
    flow_dir = tmp_path / ".forge" / "flows"
    flow_dir.mkdir(parents=True)
    (flow_dir / "standard.yml").write_text(
        "schema: forge/project-flow@1\n"
        "flow:\n"
        "  canonical: standard\n"
        "  enabled: true\n"
        "review:\n"
        "  blocking: [blocker, major]\n",
        encoding="utf-8",
    )

    result = validation.validate_project(tmp_path, PROTOCOL_ROOT)

    assert result.passed is True
    assert result.findings == ()
