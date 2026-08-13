---
forge:
  artifact: strict_review
  schema: 1
change: CHG-0001
iteration: 1
status: failed
---

# Strict Review — CHG-0001

## Iteration 1

Result: FAILED

Findings:

- BLOCKER: 0
- MAJOR: 3
- MINOR: 2
- OBSERVATION: 1

Project policy makes MAJOR findings blocking.

## REV-001 — Unsafe YAML generation for project name

Severity: MAJOR

Status: OPEN

Dimensions: correctness, configuration, compatibility

Requirements: FR-009, AC-001, AC-002

### Problem

`forge init` builds `.forge/forge.yml` through string interpolation and emits the repository directory name as an unquoted YAML scalar.

A valid repository directory can have a name such as `null`, `true`, `foo # bar`, or another YAML-significant value. The generated scalar can therefore change type, be truncated as a comment, or become syntactically invalid.

### Impact

`forge init` may return success while producing a workspace that fails `forge validate`, violating the requirement that successful initialization creates configuration conforming to the Project Schema.

### Evidence

`src/forge_cli/app.py::_workspace_files` interpolates `project_root.name` directly into `  name: ...`.

The Project Schema requires `project.name` to remain a non-empty string.

### Required direction

Generate YAML through a serializer or otherwise guarantee scalar-safe encoding. Add regression coverage using YAML-significant repository names.

---

## REV-002 — Workspace path validation is not cross-platform safe

Severity: MAJOR

Status: OPEN

Dimensions: security, filesystem, compatibility

Requirements: NFR-003, INV-003

### Problem

Workspace plans are validated with `PurePosixPath`, then applied with the host-native `Path.joinpath`.

On Windows, a raw component containing backslashes can have different semantics when converted from the POSIX validation model to a native filesystem path. A value such as a backslash-separated parent traversal is not rejected by the current `".." in path.parts` check in the POSIX model but can become structural in Windows path handling.

### Impact

The workspace boundary does not currently provide the platform-independent path-safety guarantee expected by the specification and may permit a future caller to write outside the intended staging tree on Windows.

### Required direction

Define workspace plan paths as canonical POSIX-relative paths and explicitly reject native separator ambiguity and other unsafe components before materialization. Add regression tests independent from host OS semantics.

---

## REV-003 — No-overwrite guarantee contains a cross-process race

Severity: MAJOR

Status: OPEN

Dimensions: correctness, concurrency, data integrity

Requirements: FR-007, INV-003

### Problem

`initialize_workspace` checks `target.exists()`, stages files, checks `target.exists()` again, and then calls `staging.rename(target)`.

Another process can create `.forge/` between the second existence check and the rename. The check and publication are not one exclusive operation.

### Impact

The implementation cannot strictly guarantee the MUST-level no-silent-overwrite invariant under concurrent initialization.

### Required direction

Introduce a cross-process initialization lock acquired with exclusive creation before staging. Hold it through publication and always clean it up. The lock itself must not make a failed initialization appear initialized.

---

## REV-004 — Missing Git executable does not use one consistent environment-failure path

Severity: MINOR

Status: OPEN

Dimensions: error handling, CLI contract

Requirements: FR-031

### Problem

`resolve_project_root` calls `subprocess.run` directly. If `git` is unavailable, Python raises `FileNotFoundError` instead of `NotGitRepositoryError` or another explicit environment error.

`forge init` maps this through the generic internal-error path (70), while `forge validate` can receive the exception before its generic application-error boundary.

Doctor already distinguishes Git availability explicitly.

### Impact

The CLI exposes inconsistent exit semantics for the same missing environment capability.

### Required direction

Introduce an explicit Git-unavailable error and map it to exit code 3 in commands that require Git.

---

## REV-005 — Protocol version identity is represented differently in public output and project configuration

Severity: MINOR

Status: OPEN

Dimensions: compatibility, maintainability

### Problem

`forge version` reports `Forge Protocol 1-draft`, while generated project configuration stores `forge.protocol: 1` and the runtime compatibility set contains integer `1`.

### Impact

The distinction between Protocol identity (`1`) and maturity label (`1-draft`) is implicit and could become ambiguous once migrations/version negotiation exist.

### Required direction

Centralize Protocol identity/version metadata and make the relationship explicit. This need not block the first CLI if documented before Completion.

---

## REV-006 — Initialization atomicity is process-safe but not crash-atomic

Severity: OBSERVATION

Status: OPEN

Dimensions: reliability

### Problem

Staging cleanup runs through Python exception handling. A hard process kill, machine crash, or power loss can leave `.forge.tmp-*` behind.

### Impact

The repository can retain stale staging data, although it does not appear as an initialized `.forge/` workspace and therefore does not violate FR-008 directly.

### Direction

A future `forge doctor` or `forge init` evolution may detect and report stale staging directories.

## Review gate

FAILED until REV-001, REV-002, and REV-003 are resolved and re-reviewed.
