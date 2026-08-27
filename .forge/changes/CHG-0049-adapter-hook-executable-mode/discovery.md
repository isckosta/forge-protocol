---
forge:
  artifact: discovery
  schema: 1
change: CHG-0049
status: complete
---

# Discovery — CHG-0049 Adapter Hook Executable Mode

## Executive Summary

The Adapter materialization pipeline has **no concept of file mode** at
any layer. A generated artifact is `(path, content, digest)` from
projection (`ClaudeCodeProjectionResource`) through planning
(`ProjectedArtifact`, `AdapterOperation`) to publication
(`publisher._replace_file`), which writes via a temp file + `os.replace`
and never calls `chmod`. So every materialized file, including the hook
Claude Code must `execve`, lands at the umask default (`0644`).

The narrowest correct fix threads a single `executable: bool` property
through those three layers, has the publisher apply `0o755` on POSIX for
executable operations, teaches the repository snapshot + planner to treat
"content matches but executable bit missing" as an `UPDATE` (so
`adapter update` repairs old installs), and adds one Adapter diagnostic
check. No installation-record schema change is required: the projection
remains the source of truth for which paths are executable, and the
record's `path → digest` authorization contract is unaffected.

## Investigation

### The hook and how it is invoked

- `src/forge_cli/adapters/claude_code/projection.py`
  - `_HOOK_RELATIVE_PATH = "skills/forge/hooks/check-manifest-edit.sh"`
  - `_hook_script_content()` renders a `#!/bin/sh` script.
  - `_hook_frontmatter_lines()` emits, in `SKILL.md`, three
    `PreToolUse` matchers (`Bash`, `Edit`, `Write`), each
    `- type: command` with
    `command: "${CLAUDE_PROJECT_DIR}/.claude/skills/forge/hooks/check-manifest-edit.sh"`.
  - `generate_claude_code_skill_bundle()` builds the resource tuple;
    the hook is `_resource(_HOOK_RELATIVE_PATH, _hook_script_content())`
    — identical shape to every markdown resource.
- Claude Code runs a `type: command` hook by executing the `command`
  string in a shell. The shell `execve`s the path; without an
  executable bit that fails `EACCES` → `exit 126` → hook reported failed.

### Where mode is lost — layer by layer

| Layer | Type | Mode carried? |
|---|---|---|
| Projection | `ClaudeCodeProjectionResource(name, content, digest)` | No |
| Driver → plan input | `ProjectedArtifact(path, ownership, content, merge_*)` | No |
| Planner op | `AdapterOperation(path, ownership, intent, content_digest, content, expected_current_digest)` | No |
| Repo snapshot | `RepositoryArtifactState(path, exists, current_digest, expected_digest)` — `repository._snapshot_artifact` reads only `read_text()` | No |
| Publication | `publisher._replace_file()` → `temp.write_text()` + `os.replace()`; `_restore_bytes()` on rollback | No `chmod` anywhere |
| Installation record | `state.GeneratedArtifact(path, digest)`; schema `adapter-installation@1/@2` | No |
| Drift check | `ownership.detect_generated_drift()` compares digests only | No |

### Why `adapter update` will not currently repair an old install

`service.update()` (src/forge_cli/adapters/service.py:571) early-returns
`mutated=False` when `_entirely_unchanged(plan)` **and** the recorded
adapter version equals the packaged version. For a project whose hook
content is byte-identical but mode is `0644`, the plan is all
`UNCHANGED`, so nothing is published. Even if it did publish,
`publish_adapter_plan` skips `PRESERVE`/`UNCHANGED` operations in its
mutation loop (publisher.py:508) and can early-return entirely
(publisher.py:500) when `prior_record == installation_record`.

Therefore repair requires the planner to *not* classify the hook as
`UNCHANGED` when the on-disk mode disagrees with the projection. That in
turn requires `_snapshot_artifact` to observe the executable bit and
`classify_artifact` to compare it.

### Diagnostics surface

- `AdapterService.doctor()` (service.py:227) already builds a live
  `projection` for the `conformance` check (service.py:441). A new
  `executable` check can reuse that projection: for each projected
  artifact declared executable, `stat` the on-disk file and fail if it
  exists without any `0o111` bit (POSIX only).
- `forge doctor` (`src/forge_cli/doctor/__init__.py:151`
  `_adapter_readiness_checks`) already fans every `service.doctor()`
  check out as `adapter:<id>:<check>` — a new check is surfaced there
  automatically with no wiring.
- `AdapterCheck` ids are ordered by `diagnostics._CHECK_ORDER`; a new id
  must be added there or it sorts last (still valid, just unordered).

### Cross-platform

- `os.name == "posix"` is the correct guard. On Windows `os.chmod`
  ignores executable bits and `st_mode` never reports them; the planner
  mode comparison and the doctor check must both no-op there so a
  Windows checkout is never reported as drifted/failed for a bit the
  platform does not model.
- No external dependency is needed — `os.chmod`, `os.stat`,
  `stat.S_IMODE`, `os.name` are stdlib.

### Repository-tracked mode

- `git ls-files -s .claude/skills/forge/hooks/check-manifest-edit.sh` →
  `100644`. It must become `100755` (`git update-index --chmod=+x` /
  `chmod +x` then commit). The Codex tree ships no hook
  (`grep -n "\.sh" src/forge_cli/adapters/codex/**` → nothing).
- After PR #40, `.claude/` and `.agents/` skill projections are
  in sync with Protocol sources; the only stale property is this mode.

### Existing tests to extend (not redesign)

- `tests/integration/test_adapter_publisher.py` — publisher CREATE/UPDATE
  behaviour, temp-repo based.
- `tests/unit/test_adapter_planner.py` — `plan_adapter` intent
  classification.
- `tests/unit/test_adapter_ownership.py` — `classify_artifact`.
- `tests/unit/test_claude_code_projection_bundle.py` /
  `test_claude_code_skill_projection.py` — projected resource set.
- `tests/integration/test_adapter_service.py` — install/update/doctor.
- `tests/unit/test_doctor_diagnostics.py`, `tests/cli/test_doctor.py`,
  `tests/cli/test_adapter_commands.py` — diagnostic surfacing.

## Open Questions

One material technical decision is escalated to the Plan (DEC-001):
whether to record executability in the installation record (schema bump)
or keep the projection as the single source of truth. Discovery's
finding favours the latter; the Plan records the decision and its
rationale.
