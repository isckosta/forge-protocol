"""Black-box installed-wheel acceptance probe for the Codex Adapter.

This module deliberately uses only the standard library. It imports no
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


_RUNTIME_ENVIRONMENT_KEYS = {
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_TERMINAL_PROMPT",
    "FORGE_WHEEL_GUARD_MARKER",
    "HOME",
    "LANG",
    "LC_ALL",
    "PATH",
    "PIP_CONFIG_FILE",
    "PIP_DISABLE_PIP_VERSION_CHECK",
    "PIP_NO_INDEX",
    "PYTHONNOUSERSITE",
    "TMPDIR",
    "XDG_CONFIG_HOME",
}


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


def _tree_snapshot(root: Path) -> dict[str, tuple[str, bytes | None, int]]:
    snapshot: dict[str, tuple[str, bytes | None, int]] = {
        ".": ("directory", None, root.stat().st_mtime_ns),
    }
    for path in sorted(root.rglob("*")):
        relative_path = path.relative_to(root).as_posix()
        if path.is_symlink():
            snapshot[relative_path] = ("symlink", os.readlink(path).encode(), path.lstat().st_mtime_ns)
        elif path.is_dir():
            snapshot[relative_path] = ("directory", None, path.stat().st_mtime_ns)
        elif path.is_file():
            snapshot[relative_path] = ("file", path.read_bytes(), path.stat().st_mtime_ns)
        else:
            raise AssertionError(f"unexpected repository entry: {path}")
    return snapshot


def _snapshot(paths: list[Path]) -> dict[Path, tuple[bytes, int]]:
    return {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}


def _recorded_artifacts(record: Path) -> dict[str, str]:
    pairs = re.findall(
        r"^- path: ([^\n]+)\n  digest: ([0-9a-f]{64})$",
        record.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    assert pairs, "installation record has no generated artifacts"
    paths = [path for path, _ in pairs]
    assert len(paths) == len(set(paths)), "installation record has duplicate generated paths"
    return dict(pairs)


def _with_duplicate_recorded_artifact(record_bytes: bytes) -> bytes:
    artifact = re.search(
        rb"(?m)^- path: [^\n]+\n  digest: [0-9a-f]{64}\n",
        record_bytes,
    )
    assert artifact is not None, "installation record has no artifact to duplicate"
    marker = b"limitations:\n"
    assert marker in record_bytes
    return record_bytes.replace(marker, artifact.group(0) + marker, 1)


def _assert_skill_frontmatter(skill: str) -> None:
    assert skill.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    _, frontmatter, _ = skill.split("---\n", 2)
    fields = dict(
        line.split(": ", 1)
        for line in frontmatter.splitlines()
        if ": " in line
    )
    assert fields == {
        "name": "forge",
        "description": "Use for Forge-governed engineering Changes in this repository.",
    }


def _project_flow_configuration(path: Path) -> tuple[str, bool]:
    content = path.read_text(encoding="utf-8")
    assert "schema: forge/project-flow@1\n" in content
    canonical = re.search(r"^  canonical: ([^\n]+)$", content, flags=re.MULTILINE)
    enabled = re.search(r"^  enabled: (true|false)$", content, flags=re.MULTILINE)
    assert canonical is not None, f"missing canonical Flow in {path}"
    assert enabled is not None, f"missing enabled state in {path}"
    return canonical.group(1), enabled.group(1) == "true"


def _runtime_environment() -> dict[str, str]:
    assert not os.environ.get("PYTHONPATH"), "probe runtime must not inherit PYTHONPATH"
    assert not any(
        "proxy" in key.lower() or "credential" in key.lower() or "token" in key.lower()
        for key in os.environ
    ), "probe runtime must not inherit proxy or credential variables"
    environment = {
        key: value for key, value in os.environ.items() if key in _RUNTIME_ENVIRONMENT_KEYS
    }
    assert set(environment) <= _RUNTIME_ENVIRONMENT_KEYS
    return environment


def _effective_reference_links(skill: str, skill_root: Path) -> dict[str, Path]:
    section = re.search(
        r"(?ms)^## Effective Forge references\n\n(?P<links>(?:- \[[^]]+\]\([^)]+\)\n)+)",
        skill,
    )
    assert section is not None, "SKILL.md must contain effective Forge links"
    links = re.findall(r"- \[[^]]+\]\(([^)]+)\)", section.group("links"))
    expected = [
        "references/engineering-contract.md",
        "references/flows/fast.yml",
        "references/flows/full.yml",
        "references/flows/standard.yml",
    ]
    assert links == expected
    resolved: dict[str, Path] = {}
    for link in links:
        target = (skill_root / link).resolve()
        assert target.is_relative_to(skill_root.resolve()), link
        assert target.is_file(), link
        resolved[link] = target
    return resolved


def main(
    forge_argument: str,
    repository_argument: str,
    expected_protocol_argument: str,
    expected_flows_argument: str,
    guard_marker_argument: str,
) -> None:
    forge = Path(forge_argument).resolve()
    repository = Path(repository_argument).resolve()
    expected_protocol = Path(expected_protocol_argument).resolve()
    expected_flows = Path(expected_flows_argument).resolve()
    guard_marker = Path(guard_marker_argument).resolve()
    assert forge.is_file(), forge
    assert repository.is_dir(), repository
    assert (expected_protocol / "contract" / "engineering.md").is_file()
    assert expected_flows.is_dir()

    environment = _runtime_environment()
    assert environment["FORGE_WHEEL_GUARD_MARKER"] == str(guard_marker)
    guard_marker.unlink(missing_ok=True)
    initialized = _run(forge, repository, environment, "init")
    assert initialized.stdout == f"Forge initialized at {repository / '.forge'}\n"
    assert guard_marker.read_text(encoding="utf-8") == "loaded\n"

    configuration_text = (repository / ".forge" / "forge.yml").read_text(encoding="utf-8")
    protocol_match = re.search(r"^\s*protocol:\s*(\d+)\s*$", configuration_text, re.MULTILINE)
    assert protocol_match is not None, "forge.yml must declare a Forge Protocol version"
    versioned_protocol = expected_protocol / "versions" / protocol_match.group(1)
    if not versioned_protocol.is_dir():
        versioned_protocol = expected_protocol

    flow_directory = repository / ".forge" / "flows"
    project_flow_paths = sorted(flow_directory.glob("*.yml"))
    assert {path.stem for path in project_flow_paths} == {"fast", "standard", "full"}
    project_flows = {
        path.stem: _project_flow_configuration(path) for path in project_flow_paths
    }
    enabled_canonical_flows = {
        canonical_id for canonical_id, enabled in project_flows.values() if enabled
    }
    assert enabled_canonical_flows == {"fast", "standard", "full"}
    assert all(enabled for _, enabled in project_flows.values())
    canonical_paths = [repository / ".forge" / "forge.yml", *project_flow_paths]
    canonical_before = _snapshot(canonical_paths)

    listed = _run(forge, repository, environment, "adapter", "list")
    assert "codex version=0.1.0 harness=codex" in listed.stdout
    assert "compatibility=compatible installation=not_installed" in listed.stdout

    before_plan = _tree_snapshot(repository)
    planned = _run(forge, repository, environment, "adapter", "plan", "codex")
    assert _tree_snapshot(repository) == before_plan
    before_dry_run = _tree_snapshot(repository)
    dry_run = _run(
        forge, repository, environment, "adapter", "install", "codex", "--dry-run"
    )
    assert _tree_snapshot(repository) == before_dry_run
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
    skill_root = repository / ".agents" / "skills" / "forge"
    assert {
        ".agents/skills/forge/" + path.relative_to(skill_root).as_posix()
        for path in skill_root.rglob("*")
        if path.is_file()
    } == set(artifacts)
    for relative_path, digest in artifacts.items():
        assert sha256((repository / relative_path).read_bytes()).hexdigest() == digest

    skill_path = skill_root / "SKILL.md"
    skill_bytes = skill_path.read_bytes()
    skill = skill_bytes.decode("utf-8")
    _assert_skill_frontmatter(skill)
    resolved_references = _effective_reference_links(skill, skill_root)
    contract = resolved_references["references/engineering-contract.md"]
    assert contract.read_bytes() == (versioned_protocol / "contract" / "engineering.md").read_bytes()

    generated_flow_paths = {
        path.relative_to(skill_root / "references" / "flows").with_suffix("").as_posix()
        for path in (skill_root / "references" / "flows").glob("*.yml")
    }
    assert generated_flow_paths == enabled_canonical_flows
    for flow_id in enabled_canonical_flows:
        reference = resolved_references[f"references/flows/{flow_id}.yml"]
        expected = expected_flows / f"{flow_id}.yml"
        assert reference.read_bytes() == expected.read_bytes()
        reference_text = reference.read_text(encoding="utf-8")
        assert f"flow:\n  id: {flow_id}\n" in reference_text
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
    drift_snapshot = _tree_snapshot(repository)
    drift_validation = _run(
        forge, repository, environment, "adapter", "validate", "codex", expected_exit_code=2
    )
    assert "E_FORGE_ADAPTER_DRIFT:" in drift_validation.stdout
    assert _tree_snapshot(repository) == drift_snapshot
    before_drift_update = _tree_snapshot(repository)
    drift_update = _run(
        forge, repository, environment, "adapter", "update", "codex", expected_exit_code=2
    )
    assert "E_FORGE_ADAPTER_CONFLICT:" in drift_update.stdout
    assert _tree_snapshot(repository) == before_drift_update

    skill_path.write_bytes(skill_bytes)
    restored_before_update = _tree_snapshot(repository)
    restored_update = _run(forge, repository, environment, "adapter", "update", "codex")
    assert "No changes required." in restored_update.stdout
    assert _tree_snapshot(repository) == restored_before_update
    assert {
        path: path.read_bytes() for path in [*generated_paths, record]
    } == {path: bytes_and_mtime[0] for path, bytes_and_mtime in before_reinstall.items()}
    record_bytes = record.read_bytes()
    record.write_bytes(_with_duplicate_recorded_artifact(record_bytes))
    duplicate_record_snapshot = _tree_snapshot(repository)
    duplicate_record_validation = _run(
        forge, repository, environment, "adapter", "validate", "codex", expected_exit_code=2
    )
    assert "E_FORGE_ADAPTER_INSTALLATION_INVALID:" in duplicate_record_validation.stdout
    assert _tree_snapshot(repository) == duplicate_record_snapshot
    record.write_bytes(record_bytes)
    assert _snapshot(canonical_paths) == canonical_before
    assert not (repository / ".codex").exists()


if __name__ == "__main__":
    if len(sys.argv) != 6:
        raise SystemExit(
            "usage: adapter_cli_wheel_probe.py FORGE_EXECUTABLE GIT_REPOSITORY "
            "EXPECTED_PROTOCOL_ROOT EXPECTED_EFFECTIVE_FLOW_ROOT GUARD_MARKER"
        )
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
