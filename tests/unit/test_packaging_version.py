"""Regression guard for CHG-0019's single-source-of-truth CLI version.

Strict Review R002 (CHG-0019 Iteration 1): the dynamic version-sourcing
fix (pyproject.toml's [tool.hatch.version]) was verified only by a
one-time manual `python -m build` reproduction, with no automated test.
This exercises the actual regex `hatch.version` uses, against the actual
packaged files, without the cost of a real build.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _hatch_version_config() -> dict:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return data["tool"]["hatch"]["version"]


def test_pyproject_declares_dynamic_version_sourced_from_version_py() -> None:
    data = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert data["project"].get("dynamic") == ["version"]
    assert "version" not in data["project"]

    config = _hatch_version_config()
    assert config["path"] == "src/forge_cli/version.py"


def test_hatch_version_pattern_extracts_the_real_cli_version() -> None:
    from forge_cli.version import CLI_VERSION

    config = _hatch_version_config()
    source = (REPO_ROOT / config["path"]).read_text(encoding="utf-8")

    match = re.search(config["pattern"], source)

    assert match is not None, "hatch.version pattern does not match version.py's content"
    assert match.group("version") == CLI_VERSION


def test_hatch_version_pattern_tracks_a_changed_version_string() -> None:
    """Confirms the regex is a live extraction, not one that happens to
    match only today's exact value."""
    config = _hatch_version_config()

    changed_source = 'CLI_VERSION = "9.9.9-test-only"\n'
    match = re.search(config["pattern"], changed_source)

    assert match is not None
    assert match.group("version") == "9.9.9-test-only"
