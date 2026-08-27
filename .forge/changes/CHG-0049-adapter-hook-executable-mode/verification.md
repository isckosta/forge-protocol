---
forge:
  artifact: verification
  schema: 1
change: CHG-0049
status: complete
---

# Verification — CHG-0049 Adapter Hook Executable Mode

## Result

**PASS**

## Summary

| Acceptance | Result | Evidence |
|---|---|---|
| AC-001 create lands executable (POSIX) | PASS | `test_executable_create_materializes_with_executable_mode` + in-test `subprocess` run of the script |
| AC-002 update re-applies the bit | PASS | `test_executable_update_reapplies_mode_on_identical_content` |
| AC-003 only the hook resource is executable | PASS | `test_only_the_hook_resource_is_marked_executable`, `test_claude_code_projection_renders_a_valid_repository_layout` |
| AC-004 snapshot observes the bit | PASS | `tests/unit/test_adapter_repository.py` |
| AC-005 mode-only discrepancy → `update` | PASS | `test_executable_projection_repairs_mode_only_discrepancy`, `test_executable_projection_with_non_executable_disk_state_updates` |
| AC-006 matching mode stays `unchanged` | PASS | same tests, second half; `test_non_executable_projection_ignores_disk_executable_bit` |
| AC-007 `adapter update` repairs an install, idempotently | PASS | `test_update_repairs_non_executable_hook_idempotently`, `test_adapter_doctor_flags_and_update_repairs_non_executable_hook` |
| AC-008 doctor fails + names remediation | PASS | `test_doctor_flags_non_executable_installed_hook`, `test_adapter_doctor_flags_and_update_repairs_non_executable_hook` |
| AC-009 doctor passes when healthy | PASS | `test_doctor_passes_executable_check_for_healthy_install`, `test_doctor_passes_executable_check_for_fresh_claude_code_install` |
| AC-010 `forge doctor` surfaces it | PASS | `test_doctor_flags_non_executable_claude_code_hook` |
| AC-011 hook tracked `100755` | PASS | `tests/unit/test_repository_hook_mode.py`; `git ls-files -s` |
| CON-003 non-POSIX inert | PASS | `test_executable_publish_does_not_fail_on_non_posix`, `test_doctor_executable_check_is_inert_on_non_posix` |

## Test Evidence

> **Test-evidence history (two Review iterations).** The single test that
> failed at every intermediate revision is
> `tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas`,
> which validates every canonical YAML instance against its declared
> schema. `forge validate` does NOT run this check.
>
> | Revision | Full suite | Contract | Cause |
> |---|---|---|---|
> | `ea01dc8` (impl subject) | 804 / 1 fail | 51 / 1 fail | `tdd-evidence.yml` cycle ids `TDD-C1..C5` violate `^TDD-[0-9]{3,}[A-Z]?$` (Iter 1, R-001) |
> | `e7b6b45` (Resolution 1) | 804 / 1 fail | 51 / 1 fail | ids fixed, but `manifest.yml` `review.status: in_progress` is not in the enum `[pending, active, passed, failed]` (Iter 2, R-004) |
> | Resolution 2 (this revision) | **805 / 0** | **52 / 0** | `review.status` → `active`; `review.md` frontmatter → `active` |
>
> This artifact originally asserted PASS/805 against `ea01dc8` and then
> against `e7b6b45`; both were false (Iter 1 R-002, Iter 2 R-005). The
> numbers below are the Resolution-2 run and are accurate against the
> Resolution-2 revision only.

- Full suite: `.venv/bin/python -m pytest -q` → **805 passed, 2 warnings** in ~93s.
  The 2 warnings are pre-existing and unrelated (`tests/unit/test_experience_capture.py`, FER RuntimeWarning).
  Baseline after CHG-0048 was 786; this Change adds 19 tests.
- Contract suite: `.venv/bin/python -m pytest tests/contract -q` → **52 passed**.
- New / modified test files:
  `tests/unit/test_adapter_ownership.py` (+3),
  `tests/unit/test_adapter_planner.py` (+1),
  `tests/unit/test_adapter_repository.py` (new, 2),
  `tests/integration/test_adapter_publisher.py` (+3, plus 3 monkeypatch-fake signature updates),
  `tests/integration/test_adapter_service.py` (+5, plus 1 check-id list update),
  `tests/unit/test_claude_code_projection_bundle.py` (+1),
  `tests/unit/test_claude_code_skill_projection.py` (+1 assertion block),
  `tests/cli/test_doctor.py` (+2),
  `tests/cli/test_adapter_commands.py` (+1),
  `tests/unit/test_repository_hook_mode.py` (new, 1).
- TDD RED evidence: `tdd-evidence.yml` (5 cycles; TDD-001/002 genuine RED-first, TDD-003/004/005
  disclosed as plumbing/diagnostic implemented before their pytest assertions with RED
  verified mechanically or by live command reproduction, per C-017).

## Forge Evidence

- `.venv/bin/forge validate` → **Forge project is valid** (note: `forge validate` does
  not validate canonical YAML instances against their declared schemas — that is
  `tests/contract/test_protocol_contract.py`, which is what caught R-001).
- `.venv/bin/forge adapter plan claude-code` on this repository → every artifact `UNCHANGED`
  (idempotent) after the tracked hook was set `100755`.
- `.venv/bin/forge adapter doctor claude-code` on this repository → all checks PASS, including
  `PASS executable_artifacts: Generated artifacts that must be executable are executable.`
- End-to-end, throwaway external repo (`scratchpad/repro.sh`):
  `git init` → `forge init` → `forge adapter install claude-code` →
  hook mode `0o755`, `os.access(..., X_OK)` True; piping a `sed -i ... manifest.yml`
  payload to the materialized script → `exit 0`, `permissionDecision: deny`, empty stderr.
  Confirms SC1, SC2, SC5, SC6 with no dependency on `forge-protocol` internals.
- Regression observed and fixed during Implementation: `service._prepare` dropped the newly
  observed `executable` field when rebuilding `RepositoryArtifactState`, which would have
  made the hook a perpetual mode-repair `UPDATE`. Covered by the existing
  `test_adapter_install_then_doctor_succeeds_for_every_registered_adapter[claude-code]`.

## Compatibility / Limitations

- No Protocol, schema, Contract, or Flow change. No `protocol/compatibility.md` entry.
- No installation-record schema change (DEC-001 / NFR-002).
- Non-POSIX: mode logic is gated by `plan.supports_executable_bit()`; a Windows checkout
  is never reported drifted/failed for an executable bit (CON-003). This is verified via
  `supports_executable_bit` monkeypatching, not a real Windows runner — the honest limit
  of this suite for a do-nothing-on-non-POSIX requirement.
- The Codex Adapter is untouched (ships no hook); its `executable_artifacts` check passes
  trivially ("No generated artifact requires an executable mode.").
- Live side effect: this session's own Forge `PreToolUse` hook became operative once the
  tracked hook was made executable — `Bash` commands whose text contains a
  `sed -i`/redirection pattern next to a `.forge/changes/*/manifest.yml` path are now
  denied, which is the intended behaviour restored.

## Conclusion

All 11 Acceptance Criteria and the three testable Constraints pass. The
implementation code has been byte-stable since `ea01dc8` and was audited for
correctness by the Iteration 1 Reviewer and spot-checked by the Iteration 2
Reviewer (no defect, no regression). Two Resolution rounds fixed only
Change-local evidence artifacts: Resolution 1 (R-001 cycle-id rename, R-002
evidence correction, R-003 `status: exception` TDD disclosure) and Resolution 2
(R-004 `review.status` enum fix, R-005 evidence re-correction, R-006 counter
reconciliation). At the Resolution 2 revision the full suite (805) and contract
suite (52) are green and `forge validate` passes, and the fix is demonstrated
end-to-end in a fresh external repository. Verification result: **PASS**
(against the Resolution 2 revision).
