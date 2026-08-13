from __future__ import annotations

from pathlib import Path

import yaml


FLOW_FILES = (
    Path("protocol/flows/full.yml"),
    Path("protocol/flows/standard.yml"),
    Path("protocol/flows/fast.yml"),
)


def test_all_completion_gates_require_blocking_review_threads_resolved() -> None:
    for path in FLOW_FILES:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        requirements = data["gates"]["before_completion"]["require"]
        assert "blocking_review_threads_resolved" in requirements, path.as_posix()
