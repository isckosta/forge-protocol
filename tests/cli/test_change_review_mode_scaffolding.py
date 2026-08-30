import subprocess
from pathlib import Path

import yaml
from typer.testing import CliRunner

import forge_cli.app as app_module

runner = CliRunner()


def _init_git_repository(path: Path) -> None:
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True, text=True)


def _read_forge_yml(root: Path) -> dict:
    return yaml.safe_load((root / ".forge" / "forge.yml").read_text(encoding="utf-8"))


def _write_forge_yml(root: Path, data: dict) -> None:
    (root / ".forge" / "forge.yml").write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def test_new_change_seeds_review_mode_from_project_preferred_mode(tmp_path: Path, monkeypatch) -> None:
    """CHG-0050 TDD-009 (FR-003, AC-007)."""
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app_module.app, ["init"]).exit_code == 0

    forge_yml = _read_forge_yml(tmp_path)
    forge_yml["review"]["preferred_mode"] = "thorough"
    _write_forge_yml(tmp_path, forge_yml)

    result = runner.invoke(app_module.app, ["change", "new", "sample-change"])

    assert result.exit_code == 0, result.output
    manifest = yaml.safe_load(
        (tmp_path / ".forge/changes/CHG-0001-sample-change/manifest.yml").read_text(encoding="utf-8")
    )
    assert manifest["review"]["mode"] == "thorough"


def test_new_change_defaults_review_mode_to_recommended_without_a_preference(tmp_path: Path, monkeypatch) -> None:
    """CHG-0050 TDD-010 (FR-003, AC-008)."""
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app_module.app, ["init"]).exit_code == 0

    result = runner.invoke(app_module.app, ["change", "new", "sample-change"])

    assert result.exit_code == 0, result.output
    manifest = yaml.safe_load(
        (tmp_path / ".forge/changes/CHG-0001-sample-change/manifest.yml").read_text(encoding="utf-8")
    )
    assert manifest["review"]["mode"] == "recommended"


def test_existing_change_review_mode_is_not_overridden_by_a_later_project_preference(
    tmp_path: Path, monkeypatch
) -> None:
    """CHG-0050 TDD-011 (FR-003, AC-009)."""
    _init_git_repository(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app_module.app, ["init"]).exit_code == 0
    assert runner.invoke(app_module.app, ["change", "new", "sample-change"]).exit_code == 0

    manifest_path = tmp_path / ".forge/changes/CHG-0001-sample-change/manifest.yml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["review"]["mode"] = "fast"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    forge_yml = _read_forge_yml(tmp_path)
    forge_yml["review"]["preferred_mode"] = "thorough"
    _write_forge_yml(tmp_path, forge_yml)

    validate_result = runner.invoke(app_module.app, ["validate"])

    assert validate_result.exit_code == 0, validate_result.output
    reread = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert reread["review"]["mode"] == "fast"
