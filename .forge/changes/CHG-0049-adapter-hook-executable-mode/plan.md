---
forge:
  artifact: plan
  schema: 1
change: CHG-0049
status: approved
---

# Plan — CHG-0049 Adapter Hook Executable Mode

## DEC-001 · Executability source of truth (technical, material)

The Adapter **projection** is the single source of truth for which
generated paths are executable. The `adapter-installation` record keeps
its `path → digest` shape unchanged — no schema bump.

- **Chosen:** carry `executable: bool` on the projection resource →
  `ProjectedArtifact` → `AdapterOperation`; observe the on-disk bit in the
  repository snapshot; compare the two in planning; apply in publication;
  re-derive the "should be executable" set in diagnostics from a fresh
  projection (`doctor` already builds one).
- **Rejected — add `executable` to `installation.yml` `generated_artifacts[]`
  (`adapter-installation@3`):** a Protocol-2 schema change plus a
  migration path for a property that is fully derivable from the
  projection; disproportionate to a one-artifact fix.
- **Rejected — special-case the hook path in `publisher.py`:** leaks a
  Claude-Code-specific path into the Harness-agnostic publication module;
  not reusable; violates the module's stated purpose.

No adapter `version` bump: consistent with precedent (CHG-0048 changed
`projection.py` substantially without bumping `adapter.yml`); the
content-digest drift mechanism and FR-004/FR-006 already carry the change
to existing installs.

## Work items

1. **[RED]** Add model-level scenarios first as inert field assertions,
   then behaviour: extend `tests/unit/test_adapter_plan.py` and
   `tests/unit/test_adapter_planner.py` for the new `executable` field on
   `AdapterOperation` / `ProjectedArtifact` / `RepositoryArtifactState`.
   **[GREEN]** In `src/forge_cli/adapters/plan.py`: add
   `AdapterOperation.executable: bool = False` and the `executable`
   parameter to `AdapterOperation.from_content`. In
   `src/forge_cli/adapters/planner.py`: add
   `ProjectedArtifact.executable: bool = False` and
   `RepositoryArtifactState.executable: bool = False`. (FR-001, FR-003,
   FR-004 — model)

2. **[RED]** `tests/unit/test_claude_code_projection_bundle.py` (or
   `test_claude_code_skill_projection.py`): assert exactly the
   `check-manifest-edit.sh` resource is executable (TD-004).
   **[GREEN]** In `src/forge_cli/adapters/claude_code/projection.py`: add
   `ClaudeCodeProjectionResource.executable: bool = False`, give
   `_resource()` a keyword-only `executable=False`, pass `executable=True`
   only for the `_HOOK_RELATIVE_PATH` resource. In
   `src/forge_cli/adapters/claude_code/driver.py`: pass
   `executable=resource.executable` into each `ProjectedArtifact`. (FR-002)

3. **[RED]** `tests/unit/test_adapter_repository.py` (new, or fold into an
   existing repository-snapshot test): two files, `0o755` vs `0o644`,
   POSIX-gated (TD-005).
   **[GREEN]** In `src/forge_cli/adapters/repository.py::_snapshot_artifact`:
   after the regular-file check, set
   `executable = os.name == "posix" and bool(stat.S_IMODE(target.stat().st_mode) & 0o111)`
   on the returned `RepositoryArtifactState`. Import `os`, `stat`. (FR-003)

4. **[RED]** `tests/unit/test_adapter_ownership.py` +
   `tests/unit/test_adapter_planner.py`: mode-only discrepancy →
   `UPDATE`; matching mode / non-executable / non-POSIX → `UNCHANGED`
   (TD-006, TD-007).
   **[GREEN]** In `src/forge_cli/adapters/ownership.py::classify_artifact`:
   add keyword params `desired_executable: bool = False`,
   `current_executable: bool = False`; in the FORGE_OWNED intact branch,
   `UNCHANGED` only when `desired_digest` matches **and**
   `(not desired_executable or current_executable)`, else `UPDATE`. Keep
   the module `os`-free. In `planner.py::plan_adapter`: compute
   `desired_executable = projection.executable and os.name == "posix"`,
   pass it and `current_executable=state.executable` into
   `classify_artifact`, and build the `AdapterOperation` with
   `executable=projection.executable`. (FR-004)

5. **[RED]** `tests/integration/test_adapter_publisher.py`: executable
   `create` lands `0o755`; content-identical `update` re-applies the bit;
   forced-`nt` publish does not fail / does not assert mode (TD-001,
   TD-002, TD-003). Fold the materialized-script execution check
   (`exit 0` + `deny` JSON on a crafted stdin) into TD-001.
   **[GREEN]** In `src/forge_cli/adapters/publisher.py`: `_replace_file`
   gains keyword-only `executable=False` and, when
   `executable and os.name == "posix"`, `os.chmod(temp_path, 0o755)`
   before `os.replace` (atomic — never observable non-executable). The
   `CREATE` and `UPDATE` branches of the mutation loop pass
   `executable=operation.executable`. Extend the `applied` rollback
   entries to also carry the original mode and restore it in
   `_restore_bytes` (POSIX only; `None` for created files). (FR-001)

6. **[RED]** `tests/unit/test_adapter_diagnostics.py` +
   `tests/integration/test_adapter_service.py` +
   `tests/cli/test_adapter_commands.py` + `tests/cli/test_doctor.py`:
   non-executable installed hook → `failed` check with remediation naming
   `forge adapter update claude-code`; executable hook → `passed`;
   `forge doctor` shows a failed `adapter:claude-code:` check (TD-009,
   TD-010, TD-011).
   **[GREEN]** In `src/forge_cli/adapters/diagnostics.py::_CHECK_ORDER`:
   insert `"executable_artifacts": 5` and renumber `conformance` → 6,
   `limitations` → 7. In `src/forge_cli/adapters/service.py::doctor`:
   where the live `projection` is available, add an `executable_artifacts`
   check — for each projected artifact marked `executable` (POSIX only),
   take a fresh `snapshot_repository_artifacts` for those paths and fail
   if any exists without an executable bit, remediation
   `Run \`forge adapter update {adapter_id}\``; pass otherwise; emit a
   `warning` check when `projection` is unavailable. No change needed in
   `doctor/__init__.py` (fan-out is automatic). (FR-006)

7. Make the tracked hook executable: `chmod +x
   .claude/skills/forge/hooks/check-manifest-edit.sh` and stage the
   `100644 → 100755` mode change. Confirm
   `.forge/adapters/claude-code/installation.yml` is unchanged (digest is
   content-only). **[RED/GREEN]** `tests/unit/` (new
   `test_repository_hook_mode.py` or fold into an existing distribution
   test): assert `git ls-files -s` reports `100755` for the hook
   (TD-012). (FR-007)

8. Documentation: add a `### Adapter Hook Executable Mode` entry to
   `CHANGELOG.md` `## Unreleased`. No `protocol/compatibility.md` entry
   (no Protocol/schema/Contract change). No ADR (STANDARD, contained
   technical decision recorded as DEC-001 here).

9. Verification: full `pytest -q`; `forge validate`; `forge adapter plan
   claude-code` reports every artifact `UNCHANGED` (idempotent) once the
   hook is executable on disk; materialize the Claude Code Adapter into a
   throwaway temp repo and confirm the hook file is executable and runs
   without `Permission denied`; `forge adapter doctor claude-code` and
   `forge doctor` PASS on this repository.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation.
Implementation-time discoveries belong in Verification, a new Decision
record, or a documented re-Plan — not a silent edit to this approved
Plan. RED must precede every behavioural change and must fail for the
expected reason (not a collection-time `TypeError` from a missing
kwarg — add the field inert first).

## Human Plan Authorization

This Plan is explicitly authorized by the human maintainer to proceed to
Implementation under C-077.

<!-- forge:plan-approval-confirmation -->

The user explicitly approved continuation of CHG-0049 to Implementation
in the active chat session on 2026-08-26, via `AskUserQuestion`, after
reviewing the Discovery diagnosis, DEC-001, the 9-item Plan summary, and
the 12-scenario Test Design, selecting the option "Aprovar e prosseguir".

<!-- forge:plan-approval-record -->
