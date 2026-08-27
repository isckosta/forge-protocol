"""CHG-0049 FR-007: the illustrative enforcement hook is versioned
executable, so a fresh clone of this repository (and any project that
copies it) has a working `PreToolUse` command hook."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HOOK = ".claude/skills/forge/hooks/check-manifest-edit.sh"


@pytest.mark.skipif(shutil.which("git") is None, reason="git is required")
def test_enforcement_hook_is_tracked_executable() -> None:
    output = subprocess.run(
        ["git", "ls-files", "-s", _HOOK],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert output, f"{_HOOK} is not tracked by git"
    mode = output.split(maxsplit=1)[0]
    assert mode == "100755", f"expected executable mode 100755, got {mode}"
