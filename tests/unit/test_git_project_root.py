from pathlib import Path
import subprocess

import pytest

import forge_cli.git as forge_git


def init_git_repository(path: Path) -> None:
    subprocess.run(
        ["git", "init", "--quiet", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )


def test_resolves_git_repository_root_from_root_directory(tmp_path: Path) -> None:
    init_git_repository(tmp_path)

    result = forge_git.resolve_project_root(tmp_path)

    assert result == tmp_path.resolve()


def test_resolves_same_git_repository_root_from_nested_directory(tmp_path: Path) -> None:
    init_git_repository(tmp_path)
    nested = tmp_path / "src" / "feature"
    nested.mkdir(parents=True)

    result = forge_git.resolve_project_root(nested)

    assert result == tmp_path.resolve()


def test_rejects_directory_outside_git_repository(tmp_path: Path) -> None:
    with pytest.raises(forge_git.NotGitRepositoryError):
        forge_git.resolve_project_root(tmp_path)
