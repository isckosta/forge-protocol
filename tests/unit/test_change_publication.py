"""CHG-0022 TDD-005: exclusive Change scaffold publication."""

from pathlib import Path

import pytest

from forge_cli.change_scaffolding import (
    ChangeRollbackIncompleteError,
    ScaffoldPlan,
    publish_scaffold,
)


def _plan() -> ScaffoldPlan:
    return ScaffoldPlan(files={"intent.md": "intent", "manifest.yml": "manifest"})


def test_publish_scaffold_rejects_target_appearing_after_plan_without_overwrite(
    tmp_path: Path,
) -> None:
    target = tmp_path / "CHG-0001-race"
    injected = "created by concurrent writer"

    def before_claim() -> None:
        target.mkdir()
        (target / "sentinel").write_text(injected, encoding="utf-8")

    with pytest.raises(FileExistsError):
        publish_scaffold(target, _plan(), before_claim=before_claim)

    assert (target / "sentinel").read_text(encoding="utf-8") == injected
    assert not (target / "intent.md").exists()


def test_publish_scaffold_rolls_back_files_when_file_write_fails(tmp_path: Path) -> None:
    target = tmp_path / "CHG-0001-failure"

    def fail_on_manifest(path: Path, content: str) -> None:
        if path.name == "manifest.yml":
            raise OSError("injected write failure")
        path.write_text(content, encoding="utf-8")

    with pytest.raises(OSError):
        publish_scaffold(target, _plan(), write_file=fail_on_manifest)

    assert not target.exists()


def test_publish_scaffold_preserves_content_created_by_failed_writer(tmp_path: Path) -> None:
    target = tmp_path / "changes" / "CHG-0001-race"

    def write_then_fail(path: Path, content: str) -> None:
        path.write_text("CONCURRENT", encoding="utf-8")
        raise OSError("injected failure after concurrent write")

    with pytest.raises(ChangeRollbackIncompleteError):
        publish_scaffold(target, ScaffoldPlan(files={"intent.md": "owned"}), write_file=write_then_fail)

    assert (target / "intent.md").read_text(encoding="utf-8") == "CONCURRENT"
