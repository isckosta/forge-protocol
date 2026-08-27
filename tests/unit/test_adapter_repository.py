from __future__ import annotations

import os
from pathlib import Path

import pytest

from forge_cli.adapters.repository import snapshot_repository_artifacts

posix_only = pytest.mark.skipif(
    os.name != "posix", reason="executable-bit observation is POSIX-only"
)


@posix_only
def test_snapshot_reports_executable_bit_per_regular_file(tmp_path: Path) -> None:
    executable = tmp_path / "hook.sh"
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)

    plain = tmp_path / "note.md"
    plain.write_text("plain\n", encoding="utf-8")
    plain.chmod(0o644)

    snapshot = snapshot_repository_artifacts(tmp_path, ("hook.sh", "note.md"))

    assert snapshot.artifacts["hook.sh"].executable is True
    assert snapshot.artifacts["note.md"].executable is False


@posix_only
def test_snapshot_requires_the_owner_execute_bit(tmp_path: Path) -> None:
    # 0o655: group/other execute set, owner NOT -- the owning user cannot
    # execute it, so it must be reported non-executable (PR #41 Codex P1).
    owner_stripped = tmp_path / "hook.sh"
    owner_stripped.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    owner_stripped.chmod(0o655)

    snapshot = snapshot_repository_artifacts(tmp_path, ("hook.sh",))

    assert snapshot.artifacts["hook.sh"].executable is False


@posix_only
def test_snapshot_reports_missing_file_as_non_executable(tmp_path: Path) -> None:
    snapshot = snapshot_repository_artifacts(tmp_path, ("absent.sh",))

    state = snapshot.artifacts["absent.sh"]
    assert state.exists is False
    assert state.executable is False
