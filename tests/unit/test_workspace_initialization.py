from pathlib import Path

import pytest

from forge_cli import workspace


def test_initializes_forge_workspace_with_requested_files(tmp_path: Path) -> None:
    workspace.initialize_workspace(
        tmp_path,
        {
            "forge.yml": "schema: forge/project@1\n",
            "contract/engineering.md": "# Project Contract\n",
        },
    )

    assert (tmp_path / ".forge" / "forge.yml").read_text() == "schema: forge/project@1\n"
    assert (tmp_path / ".forge" / "contract" / "engineering.md").read_text() == "# Project Contract\n"


def test_rejects_existing_forge_workspace_without_modifying_it(tmp_path: Path) -> None:
    forge_dir = tmp_path / ".forge"
    forge_dir.mkdir()
    existing = forge_dir / "forge.yml"
    existing.write_text("existing\n")

    with pytest.raises(workspace.WorkspaceAlreadyInitializedError):
        workspace.initialize_workspace(tmp_path, {"forge.yml": "replacement\n"})

    assert existing.read_text() == "existing\n"


def test_failed_initialization_does_not_publish_partial_workspace(tmp_path: Path) -> None:
    with pytest.raises(workspace.InvalidWorkspacePlanError):
        workspace.initialize_workspace(
            tmp_path,
            {
                "conflict": "file\n",
                "conflict/forge.yml": "nested\n",
            },
        )

    assert not (tmp_path / ".forge").exists()
    assert not any(tmp_path.glob(".forge.tmp-*"))
