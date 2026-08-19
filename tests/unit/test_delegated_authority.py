"""CHG-0015: delegated Execution authority (C-060-C-066).

Mirrors the real-Git-repository style already used by
tests/unit/test_resolution_verification.py: scenarios that need to prove a
real Git-observable mutation was (or was not) detected are built from real
commits and real working-tree state, not mocked.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import jsonschema
import pytest
import yaml

from forge_cli.protocol_resources import resolve_protocol_root
from forge_cli.validation import validate_project

BASE_FORGE_YML = """schema: forge/project@1
project:
  name: t
forge:
  protocol: 2
flows:
  default: full
  allow_fast: true
  auto_escalation: true
testing:
  approach: tdd_first
review:
  strict: true
documentation:
  impact_evaluation: required
"""

_DELEGATED_CODES = {"C-060", "C-061", "C-062", "C-063", "C-064", "C-065", "C-066"}


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def _init_repo(root: Path) -> None:
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@x")
    _git(root, "config", "user.name", "T")
    forge = root / ".forge"
    forge.mkdir()
    (forge / "forge.yml").write_text(BASE_FORGE_YML, encoding="utf-8")


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _hash_object(root: Path, rel: str) -> str:
    q = subprocess.run(["git", "hash-object", rel], cwd=root, capture_output=True, text=True, check=True)
    return q.stdout.strip()


def _dirty_snapshot(root: Path) -> list[dict]:
    staged = subprocess.run(["git", "diff", "--name-only", "--cached"], cwd=root, capture_output=True, text=True, check=True).stdout.split()
    unstaged = subprocess.run(["git", "diff", "--name-only"], cwd=root, capture_output=True, text=True, check=True).stdout.split()
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root, capture_output=True, text=True, check=True).stdout.split()
    paths = sorted(set(staged) | set(unstaged) | set(untracked))
    out: list[dict] = []
    for p in paths:
        full = root / p
        if full.exists() and full.is_file():
            out.append({"path": p, "hash": _hash_object(root, p)})
    return out


def _baseline(root: Path) -> dict:
    head = _git(root, "rev-parse", "HEAD").stdout.strip()
    return {"head": head, "dirty": _dirty_snapshot(root)}


def _primary_record(record_id: str, commit: str, scope: list[str] | None = None) -> dict:
    rec = {
        "id": record_id,
        "role": "implementation",
        "execution": {"id": f"{record_id}-exec", "context_id": f"{record_id}-ctx"},
        "recorded_at": "2026-08-19T00:00:00Z",
        "revision": {"id": f"{record_id}-rev", "immutable_ref": {"type": "git_commit", "value": commit}, "commit": commit},
        "source": {"assurance": "recorded", "observed_by": "self"},
    }
    if scope is not None:
        rec["scope"] = scope
    return rec


def _delegated_record(record_id: str, scope: list[str], baseline: dict, delegated_by: str, close_commit: str) -> dict:
    return {
        "id": record_id,
        "role": "delegated_task",
        "execution": {"id": f"{record_id}-exec", "context_id": f"{record_id}-ctx", "delegated_by": delegated_by},
        "recorded_at": "2026-08-19T00:00:00Z",
        "scope": scope,
        "baseline": baseline,
        "revision": {"id": f"{record_id}-rev", "immutable_ref": {"type": "git_commit", "value": close_commit}, "commit": close_commit},
        "source": {"assurance": "recorded", "observed_by": "self"},
    }


def _provenance(change_id: str, records: list[dict]) -> dict:
    return {"schema": "forge/execution-provenance@2", "change": change_id, "records": records}


def _manifest(change_id: str) -> dict:
    return {
        "schema": "forge/change@2",
        "protocol": 2,
        "change": {"id": change_id, "title": "T", "kind": "feature"},
        "flow": {"initial": "full", "current": "full", "escalations": []},
        "state": {"current": "implementation"},
        "artifacts": {},
        "tdd": {"status": "compliant", "cycles": 1},
        "verification": {"status": "passed"},
        "review": {"status": "pending", "iteration": 0, "blockers": 0, "majors": 0, "minors": 0, "observations": 0, "iterations": []},
        "documentation": {"impact_evaluated": True, "update_required": False},
    }


def _write_metadata(root: Path, change_dir: str, manifest: dict, provenance: dict) -> None:
    change = root / ".forge/changes" / change_dir
    change.mkdir(parents=True, exist_ok=True)
    (change / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    (change / "provenance.yml").write_text(yaml.safe_dump(provenance, sort_keys=False), encoding="utf-8")


def _codes(result) -> list[str]:
    return [f.code for f in result.findings if f.code in _DELEGATED_CODES]


def _messages(result) -> list[str]:
    return [f.message for f in result.findings if f.code in _DELEGATED_CODES]


# ---------------------------------------------------------------------------
# TDD-001 -- legacy/compatibility baseline: no delegated_task record exists
# anywhere in this repository's own history yet.
# ---------------------------------------------------------------------------

def test_legacy_repository_is_unaffected() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = validate_project(repo_root, resolve_protocol_root())
    assert _codes(result) == [], _messages(result)


# ---------------------------------------------------------------------------
# TDD-002 -- pure read-only delegate that only reads (golden path).
# ---------------------------------------------------------------------------

def test_read_only_delegate_that_only_reads(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    _write(root, "docs/x.md", "hello\n")
    open_commit = _commit(root, "seed")
    baseline = _baseline(root)
    close_commit = open_commit
    manifest = _manifest("CHG-9001")
    provenance = _provenance("CHG-9001", [
        _primary_record("impl-001", open_commit),
        _delegated_record("deleg-001", [], baseline, "impl-001", close_commit),
    ])
    _write_metadata(root, "CHG-9001-golden", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == [], _messages(result)


# ---------------------------------------------------------------------------
# TDD-003 -- the incident class (AC-012). Mechanically reproduces CHG-0014's
# actual incident shape: a primary Execution mid-Discovery, with its own
# genuine pre-existing dirty file, delegates read-only to a subagent that
# overwrites intent.md anyway.
# ---------------------------------------------------------------------------

def test_incident_class_read_only_delegate_writes_outside_scope(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    _write(root, "intent.md", "original intent\n")
    _write(root, "discovery.md", "v1\n")
    open_commit = _commit(root, "seed")
    # Primary Execution's own pre-existing, unrelated dirty edit -- present
    # BEFORE baseline is captured, exactly as in the real incident.
    _write(root, "discovery.md", "v1 + primary's own draft edit\n")
    baseline = _baseline(root)
    assert any(d["path"] == "discovery.md" for d in baseline["dirty"])
    # The delegate (scope: [], read-only) overwrites intent.md directly,
    # uncommitted -- the exact incident action.
    _write(root, "intent.md", "overwritten by subagent\n")
    close_commit = open_commit
    manifest = _manifest("CHG-9002")
    provenance = _provenance("CHG-9002", [
        _primary_record("impl-001", open_commit),
        _delegated_record("deleg-001", [], baseline, "impl-001", close_commit),
    ])
    _write_metadata(root, "CHG-9002-incident", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == ["C-061"], _messages(result)
    assert any("intent.md" in m for m in _messages(result))
    assert not any("discovery.md" in m for m in _messages(result))


# ---------------------------------------------------------------------------
# TDD-004 -- scoped writer within declared paths (golden path).
# ---------------------------------------------------------------------------

def test_scoped_writer_within_declared_paths(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    _write(root, "tests/fixtures/example.py", "v1\n")
    open_commit = _commit(root, "seed")
    baseline = _baseline(root)
    _write(root, "tests/fixtures/example.py", "v2\n")
    close_commit = open_commit
    manifest = _manifest("CHG-9003")
    provenance = _provenance("CHG-9003", [
        _primary_record("impl-001", open_commit, scope=["tests/fixtures/example.py"]),
        _delegated_record("deleg-001", ["tests/fixtures/example.py"], baseline, "impl-001", close_commit),
    ])
    _write_metadata(root, "CHG-9003-scoped", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == [], _messages(result)


# ---------------------------------------------------------------------------
# TDD-005 -- scoped writer partially outside declared paths.
# ---------------------------------------------------------------------------

def test_scoped_writer_partially_outside_declared_paths(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    _write(root, "tests/fixtures/example.py", "v1\n")
    _write(root, "src/forge_cli/unrelated.py", "v1\n")
    open_commit = _commit(root, "seed")
    baseline = _baseline(root)
    _write(root, "tests/fixtures/example.py", "v2\n")
    _write(root, "src/forge_cli/unrelated.py", "v2\n")
    close_commit = open_commit
    manifest = _manifest("CHG-9004")
    provenance = _provenance("CHG-9004", [
        _primary_record("impl-001", open_commit, scope=["tests/fixtures/example.py"]),
        _delegated_record("deleg-001", ["tests/fixtures/example.py"], baseline, "impl-001", close_commit),
    ])
    _write_metadata(root, "CHG-9004-partial", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == ["C-061"], _messages(result)
    assert any("unrelated.py" in m for m in _messages(result))
    assert not any("example.py" in m for m in _messages(result))


# ---------------------------------------------------------------------------
# TDD-006 -- self-authorization: a delegate rewrites its own already-
# committed provenance scope to claim a broader grant. Regression test for
# the two Architecture-stage corrections (commits d1ec5e8, c7ffb47).
# ---------------------------------------------------------------------------

def test_self_authorization_rewriting_own_scope(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    open_commit = _commit(root, "seed")
    baseline = _baseline(root)
    close_commit = open_commit
    manifest = _manifest("CHG-9005")
    provenance_v1 = _provenance("CHG-9005", [
        _primary_record("impl-001", open_commit),
        _delegated_record("deleg-001", [], baseline, "impl-001", close_commit),
    ])
    _write_metadata(root, "CHG-9005-selfauth", manifest, provenance_v1)
    _commit(root, "record delegation with scope: []")
    # The delegate rewrites its OWN record's scope, uncommitted, to claim a
    # write grant it was never actually given.
    provenance_v2 = _provenance("CHG-9005", [
        _primary_record("impl-001", open_commit),
        _delegated_record("deleg-001", [".forge/changes/CHG-9005-selfauth/discovery.md"], baseline, "impl-001", close_commit),
    ])
    _write_metadata(root, "CHG-9005-selfauth", manifest, provenance_v2)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == ["C-062"], _messages(result)


# ---------------------------------------------------------------------------
# TDD-007 -- Delegation Ceiling, first hop, conservative default exceeded.
# ---------------------------------------------------------------------------

def test_delegation_ceiling_conservative_default_exceeded(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    _write(root, "docs/unrelated.md", "x\n")
    open_commit = _commit(root, "seed")
    baseline = _baseline(root)
    close_commit = open_commit
    manifest = _manifest("CHG-9006")
    provenance = _provenance("CHG-9006", [
        _primary_record("impl-001", open_commit),  # no scope declared
        _delegated_record("deleg-001", ["docs/unrelated.md"], baseline, "impl-001", close_commit),
    ])
    _write_metadata(root, "CHG-9006-ceiling", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == ["C-063"], _messages(result)


# ---------------------------------------------------------------------------
# TDD-008 -- Delegation Ceiling, first hop, within conservative default.
# ---------------------------------------------------------------------------

def test_delegation_ceiling_within_conservative_default(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    open_commit = _commit(root, "seed")
    baseline = _baseline(root)
    close_commit = open_commit
    manifest = _manifest("CHG-9007")
    provenance = _provenance("CHG-9007", [
        _primary_record("impl-001", open_commit),
        _delegated_record("deleg-001", [".forge/changes/CHG-9007-ceiling-ok/discovery.md"], baseline, "impl-001", close_commit),
    ])
    _write_metadata(root, "CHG-9007-ceiling-ok", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == [], _messages(result)


# ---------------------------------------------------------------------------
# TDD-009 -- nested delegation narrows correctly.
# ---------------------------------------------------------------------------

def test_nested_delegation_narrows_correctly(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    _write(root, "src/a/f1.py", "x\n")
    _write(root, "src/a/f2.py", "y\n")
    open_commit = _commit(root, "seed")
    baseline = _baseline(root)
    close_commit = open_commit
    manifest = _manifest("CHG-9008")
    provenance = _provenance("CHG-9008", [
        _primary_record("impl-001", open_commit, scope=["src/a/f1.py", "src/a/f2.py"]),
        _delegated_record("deleg-a", ["src/a/f1.py", "src/a/f2.py"], baseline, "impl-001", close_commit),
        _delegated_record("deleg-b", ["src/a/f1.py"], baseline, "deleg-a", close_commit),
    ])
    _write_metadata(root, "CHG-9008-nested", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == [], _messages(result)


# ---------------------------------------------------------------------------
# TDD-010 -- nested delegation attempts to widen.
# ---------------------------------------------------------------------------

def test_nested_delegation_attempts_to_widen(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    _write(root, "src/a/f1.py", "x\n")
    open_commit = _commit(root, "seed")
    baseline = _baseline(root)
    close_commit = open_commit
    manifest = _manifest("CHG-9009")
    provenance = _provenance("CHG-9009", [
        _primary_record("impl-001", open_commit, scope=["src/a/f1.py"]),
        _delegated_record("deleg-a", ["src/a/f1.py"], baseline, "impl-001", close_commit),
        _delegated_record("deleg-b", ["src/a/f1.py", "src/b/f2.py"], baseline, "deleg-a", close_commit),
    ])
    _write_metadata(root, "CHG-9009-widen", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == ["C-063"], _messages(result)


# ---------------------------------------------------------------------------
# TDD-011 -- missing delegator reference (provenance gap, fail-closed).
# ---------------------------------------------------------------------------

def test_missing_delegator_reference(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    open_commit = _commit(root, "seed")
    baseline = _baseline(root)
    manifest = _manifest("CHG-9010")
    provenance = _provenance("CHG-9010", [
        _delegated_record("deleg-001", [], baseline, "nonexistent-record", open_commit),
    ])
    _write_metadata(root, "CHG-9010-gap", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == ["C-065"], _messages(result)


# ---------------------------------------------------------------------------
# TDD-012 -- fail-closed on unavailable baseline history (C-065/INV-005).
# ---------------------------------------------------------------------------

def test_fail_closed_on_unavailable_baseline_history(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    open_commit = _commit(root, "seed")
    baseline = {"head": "0" * 40, "dirty": []}  # a commit that does not exist locally
    manifest = _manifest("CHG-9011")
    provenance = _provenance("CHG-9011", [
        _primary_record("impl-001", open_commit),
        _delegated_record("deleg-001", [], baseline, "impl-001", open_commit),
    ])
    _write_metadata(root, "CHG-9011-shallow", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == ["C-065"], _messages(result)


# ---------------------------------------------------------------------------
# TDD-013 -- delegated_task record missing scope entirely (shape, C-060).
# ---------------------------------------------------------------------------

def test_delegated_task_missing_scope_is_a_finding(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    open_commit = _commit(root, "seed")
    baseline = _baseline(root)
    manifest = _manifest("CHG-9012")
    deleg_no_scope = {
        "id": "deleg-001",
        "role": "delegated_task",
        "execution": {"id": "deleg-001-exec", "context_id": "deleg-001-ctx", "delegated_by": "impl-001"},
        "recorded_at": "2026-08-19T00:00:00Z",
        "baseline": baseline,
        "revision": {"id": "deleg-001-rev", "immutable_ref": {"type": "git_commit", "value": open_commit}, "commit": open_commit},
        "source": {"assurance": "recorded", "observed_by": "self"},
    }
    provenance = _provenance("CHG-9012", [_primary_record("impl-001", open_commit), deleg_no_scope])
    _write_metadata(root, "CHG-9012-noscope", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == ["C-060"], _messages(result)


# ---------------------------------------------------------------------------
# TDD-014 -- schema-level scope: [] acceptance (forge/execution-
# provenance@2), and confirmation @1 still rejects it.
# ---------------------------------------------------------------------------

def test_v2_schema_accepts_empty_scope_v1_still_rejects_it() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    v2 = json.loads((repo_root / "protocol/schemas/execution-provenance-v2.schema.json").read_text(encoding="utf-8"))
    v1 = json.loads((repo_root / "protocol/schemas/execution-provenance.schema.json").read_text(encoding="utf-8"))
    commit = "a" * 40
    record_v2 = {
        "schema": "forge/execution-provenance@2", "change": "CHG-9013",
        "records": [{
            "id": "deleg-001", "role": "delegated_task",
            "execution": {"id": "e", "context_id": "c", "delegated_by": "impl-001"},
            "recorded_at": "2026-08-19T00:00:00Z",
            "scope": [],
            "baseline": {"head": commit, "dirty": []},
            "revision": {"id": "r", "immutable_ref": {"type": "git_commit", "value": commit}},
            "source": {"assurance": "recorded", "observed_by": "self"},
        }],
    }
    jsonschema.Draft202012Validator(v2).validate(record_v2)
    record_v1 = {
        "schema": "forge/execution-provenance@1", "change": "CHG-9013",
        "records": [{
            "id": "impl-001", "role": "implementation",
            "execution": {"id": "e", "context_id": "c"},
            "recorded_at": "2026-08-19T00:00:00Z",
            "scope": [],
            "revision": {"id": "r", "immutable_ref": {"type": "git_commit", "value": commit}},
            "source": {"assurance": "recorded", "observed_by": "self"},
        }],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(v1).validate(record_v1)


# ---------------------------------------------------------------------------
# TDD-015 -- absence of provenance.yml entirely (compatibility, distinct
# from TDD-001's real-historical-files case).
# ---------------------------------------------------------------------------

def test_absent_provenance_file_is_unaffected(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    _commit(root, "seed")
    manifest = _manifest("CHG-9014")
    change = root / ".forge/changes/CHG-9014-noprov"
    change.mkdir(parents=True)
    (change / "manifest.yml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result) == [], _messages(result)


# ---------------------------------------------------------------------------
# TDD-016 -- malformed baseline shape is a finding, not a silent pass or a
# crash (fail-closed on structurally invalid input).
# ---------------------------------------------------------------------------

def test_malformed_baseline_is_a_finding(tmp_path: Path) -> None:
    root = tmp_path
    _init_repo(root)
    open_commit = _commit(root, "seed")
    manifest = _manifest("CHG-9015")
    provenance = _provenance("CHG-9015", [
        _primary_record("impl-001", open_commit),
        _delegated_record("deleg-001", [], {"head": open_commit, "dirty": "not-a-list"}, "impl-001", open_commit),
    ])
    _write_metadata(root, "CHG-9015-malformed", manifest, provenance)
    result = validate_project(root, resolve_protocol_root())
    assert _codes(result), _messages(result)
