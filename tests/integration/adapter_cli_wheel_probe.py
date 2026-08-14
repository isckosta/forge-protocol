"""Black-box installed-wheel acceptance probe for the Codex Adapter.

This module deliberately uses only the standard library.  It imports no
checkout helpers and interacts with Forge exclusively through the supplied
installed ``forge`` executable.
"""

from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import re
import subprocess
import sys


def _run(
    forge: Path,
    repository: Path,
    environment: dict[str, str],
    *arguments: str,
    expected_exit_code: int = 0,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [str(forge), *arguments],
        cwd=repository,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != expected_exit_code:
        command = " ".join(("forge", *arguments))
        raise AssertionError(
            f"{command} returned {completed.returncode}, expected {expected_exit_code}.\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return completed


def _operation_lines(output: str) -> list[str]:
    operations = {
        "CREATE",
        "UPDATE",
        "UNCHANGED",
        "PRESERVE",
        "CONFLICT",
        "DELETE_GENERATED",
    }
    return [
        line for line in output.splitlines() if line.split(" ", 1)[0] in operations
    ]


def _snapshot(paths: list[Path]) -> dict[Path, tuple[bytes, int]]:
    return {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}


def _recorded_artifacts(record: Path) -> dict[str, str]:
    pairs = re.findall(
        r"^- path: ([^\n]+)\n  digest: ([0-9a-f]{64})$",
        record.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    assert pairs, "installation record has no generated artifacts"
    return dict(pairs)


def _assert_skill_frontmatter(skill: str) -> None:
    assert skill.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    _, frontmatter, _ = skill.split("---\n", 2)
    fields = dict(
        line.split(": ", 1)
        for line in frontmatter.splitlines()
        if ": " in line
    )
    assert fields.get("name") == "forge"
    assert fields.get("description")


def main(forge_argument: str, repository_argument: str) -> None:
    forge = Path(forge_argument).resolve()
    repository = Path(repository_argument).resolve()
    assert forge.is_file(), forge
    assert repository.is_dir(), repository

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("VIRTUAL_ENV", None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PIP_NO_INDEX"] = "1"
    environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    environment["PIP_CONFIG_FILE"] = os.devnull

    initialized = _run(forge, repository, environment, "init")
    assert "Forge initialized at" in initialized.stdout
    canonical_paths = [
        repository / ".forge" / "forge.yml",
        *(sorted((repository / ".forge" / "flows").glob("*.yml"))),
    ]
    canonical_before = {path: path.read_bytes() for path in canonical_paths}

    listed = _run(forge, repository, environment, "adapter", "list")
    assert "codex version=0.1.0 harness=codex" in listed.stdout
    assert "compatibility=compatible installation=not_installed" in listed.stdout

    planned = _run(forge, repository, environment, "adapter", "plan", "codex")
    dry_run = _run(
        forge, repository, environment, "adapter", "install", "codex", "--dry-run"
    )
    assert _operation_lines(planned.stdout) == _operation_lines(dry_run.stdout)
    assert _operation_lines(planned.stdout)
    assert not (repository / ".agents").exists()

    installed = _run(forge, repository, environment, "adapter", "install", "codex")
    assert _operation_lines(installed.stdout) == _operation_lines(planned.stdout)
    record = repository / ".forge" / "adapters" / "codex" / "installation.yml"
    assert record.is_file()
    artifacts = _recorded_artifacts(record)
    generated_paths = [repository / relative_path for relative_path in artifacts]
    assert all(path.is_file() for path in generated_paths)
    assert {
        ".agents/skills/forge/" + path.relative_to(repository / ".agents" / "skills" / "forge").as_posix()
        for path in (repository / ".agents" / "skills" / "forge").rglob("*")
        if path.is_file()
    } == set(artifacts)
    for relative_path, digest in artifacts.items():
        assert sha256((repository / relative_path).read_bytes()).hexdigest() == digest

    skill_path = repository / ".agents" / "skills" / "forge" / "SKILL.md"
    skill_bytes = skill_path.read_bytes()
    skill = skill_bytes.decode("utf-8")
    _assert_skill_frontmatter(skill)
    assert "references/engineering-contract.md" not in skill
    contract = repository / ".agents" / "skills" / "forge" / "references" / "engineering-contract.md"
    assert "Status: Canonical Protocol 1 Contract" in contract.read_text(encoding="utf-8")
    for flow_id in ("fast", "standard", "full"):
        flow = repository / ".agents" / "skills" / "forge" / "references" / "flows" / f"{flow_id}.yml"
        assert flow.is_file()
        assert f"id: {flow_id}" in flow.read_text(encoding="utf-8")
        assert f"### Flow `{flow_id}` gate obligations" in skill

    before_reinstall = _snapshot([*generated_paths, record])
    reinstalled = _run(forge, repository, environment, "adapter", "install", "codex")
    assert "No changes required." in reinstalled.stdout
    assert all(line.startswith("UNCHANGED forge_owned ") for line in _operation_lines(reinstalled.stdout))
    assert _snapshot([*generated_paths, record]) == before_reinstall

    validated = _run(forge, repository, environment, "adapter", "validate", "codex")
    assert validated.stdout == "Adapter installation is valid\n"
    diagnosed = _run(forge, repository, environment, "adapter", "doctor", "codex")
    assert "PASS generated_drift:" in diagnosed.stdout
    assert "PASS conformance:" in diagnosed.stdout

    skill_path.write_bytes(skill_bytes + b"\n# deliberate generated drift\n")
    drift_snapshot = _snapshot([*generated_paths, record])
    drift_validation = _run(
        forge, repository, environment, "adapter", "validate", "codex", expected_exit_code=2
    )
    assert "E_FORGE_ADAPTER_DRIFT:" in drift_validation.stdout
    drift_update = _run(
        forge, repository, environment, "adapter", "update", "codex", expected_exit_code=2
    )
    assert "E_FORGE_ADAPTER_CONFLICT:" in drift_update.stdout
    assert _snapshot([*generated_paths, record]) == drift_snapshot

    skill_path.write_bytes(skill_bytes)
    restored_before_update = _snapshot([*generated_paths, record])
    restored_update = _run(forge, repository, environment, "adapter", "update", "codex")
    assert "No changes required." in restored_update.stdout
    assert _snapshot([*generated_paths, record]) == restored_before_update
    assert {
        path: path.read_bytes() for path in [*generated_paths, record]
    } == {path: bytes_and_mtime[0] for path, bytes_and_mtime in before_reinstall.items()}
    assert {path: path.read_bytes() for path in canonical_paths} == canonical_before
    assert not (repository / ".codex").exists()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: adapter_cli_wheel_probe.py FORGE_EXECUTABLE GIT_REPOSITORY")
    main(sys.argv[1], sys.argv[2])
