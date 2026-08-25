---
forge:
  artifact: verification
  schema: 1
change: CHG-0046
status: complete
---

# CHG-0046 · Verification

## Result

**PASS**

## Summary

All 5 Acceptance Criteria (AC-001 through AC-005) verified and passing.
Both Functional Requirements (FR-001, FR-002) implemented via 5 TDD
cycles, each RED-before-GREEN for the expected reason where a behavior
change was under test (TDD-001, TDD-004), and passing unmodified as
guard/characterization evidence where no behavior change was expected
(TDD-002, TDD-003, TDD-005). The Specification-level acceptance check —
reproducing CHG-0045's actual PR #36 base/head commits against this
Change's implementation — confirms MR-015 and MR-017 no longer appear;
MR-006 and MR-008 still appear, exactly as Success Criteria predicted (Out
of Scope, CHG-0045's own bookkeeping).

## Acceptance Coverage

| Acceptance | Requirement | Result | Evidence |
|---|---|---|---|
| AC-001 | FR-001 | PASS | TDD-001 (`test_merge_check_tolerates_change_local_artifact_after_completion`) |
| AC-002 | FR-001 (bounded, not claimed) | PASS | TDD-003 (`test_merge_check_does_not_detect_external_drift_after_completion`) — characterization, confirms this Change's blast radius stays inside `change_root` |
| AC-003 | FR-001 | PASS | TDD-002 (`test_merge_check_still_flags_change_local_edit_before_completion`) |
| AC-004 | FR-002 | PASS | TDD-004 (`test_agent_adapter_generated_paths_resolve_to_a_definite_classification`, 10 parametrized cases) |
| AC-005 | FR-002 | PASS | TDD-005 (`test_unrelated_unclassified_path_still_falls_back_to_ambiguous`) plus pre-existing `test_ambiguous_unclassified_diff_is_blocked` (unmodified, still passing) |

## Test Evidence

- TDD-001: RED confirmed against unmodified `evaluator.py` — `MR-015` present in stdout, exit code 1 (reproducing CHG-0045/PR-#36's exact failure as a minimal fixture). GREEN after implementing the `state.current == "complete"` conditional in `_check_change()` (`evaluator.py:145-150`) — `MR-015` absent, `MERGE READY`, exit code 0.
- TDD-002: passes unmodified before and after the fix (guard test, not a RED cycle — Architecture's design does not change this path). Confirms the `state.current` boundary is real, not a no-op.
- TDD-003: passes unmodified before and after the fix (characterization test of the pre-existing, Out-of-Scope gap — Discovery/Specification). Confirms this Change does not regress or accidentally alter `change_root`-external handling in either direction.
- TDD-004: RED confirmed against unmodified `protocol/policies/merge-readiness.yml` — all 10 parametrized cases return `ambiguous`. GREEN after adding 3 `material_prefixes` entries and 1 `material_paths` entry — all 10 return `material`.
- TDD-005: passes unmodified before and after (fail-closed fallback guard).
- Full suite: `.venv/bin/python -m pytest -q` → `702 passed, 2 warnings` (both warnings pre-existing, `tests/unit/test_experience_capture.py`, unrelated to this Change — FER capture-failure logging tests, not a real failure).
- `tests/cli/test_merge_check.py` alone: `11 passed` (8 pre-existing + 3 new; no pre-existing test modified).
- `tests/unit/test_merge_readiness_policy.py` (new file): `11 passed` (10 parametrized + 1).

## Forge Evidence

- `forge validate` → `Forge project is valid`.
- `forge doctor` → all `PASS` except two pre-existing, unrelated `WARN`s (`adapter:installation_missing` — no Adapter installed on this branch, expected since it forked from `main` before CHG-0045 merges any Adapter changes; `migration_available` — 6 pre-existing migration candidates, unrelated to this Change's files).
- Specification-level acceptance check (Success Criteria), run from a disposable `git worktree` checked out at CHG-0045's actual PR #36 head commit (`9f49c13761be6c3779045b3a186c3aeaccaff938`), using this Change's modified `evaluator.py`/`merge-readiness.yml` (loaded via the editable install's absolute source path, independent of the worktree's own checked-out content):

  ```
  $ forge change merge-check --base 3aa195539218b8902296ff37f043359dd6e2614c --head 9f49c13761be6c3779045b3a186c3aeaccaff938
  Forge Merge Readiness
  Base: 3aa195539218b8902296ff37f043359dd6e2614c
  Head: 9f49c13761be6c3779045b3a186c3aeaccaff938
  FAIL MR-006 [CHG-0045]: Verification evidence is not bound to the immutable implementation subject
  FAIL MR-008 [CHG-0045]: PLAN AUTHORIZATION STALE
  MERGE BLOCKED
  ```

  Before this Change (recorded in Discovery): `MR-017` (×10), `MR-015`,
  `MR-006`, `MR-008` all failed. After: only `MR-006`/`MR-008` remain —
  exactly the two genuine CHG-0045-side provenance gaps Discovery
  identified as Out of Scope. `MR-015` and `MR-017` are gone.

## Compatibility and Limitations

No Protocol version change; no artifact schema change. No other code in
`src/` reads `merge_readiness/evaluator.py` or
`protocol/policies/merge-readiness.yml` outside the `merge_readiness`
package itself and its CLI wiring (`change_cli.py`) — confirmed by
`grep -rl` across `src/` during Plan item 8. This Change does not, and
does not claim to, close the separate pre-existing gap TDD-003
characterizes (no protection against a completed Change's implementation
changing outside its own `change_root`) — recorded as Out of Scope and
flagged separately (not fixed here).

## Conclusion

FR-001 and FR-002 fully implemented and verified against their Specification
Acceptance Criteria. No regression in the existing `tests/cli/test_merge_check.py`
suite or the wider `pytest` suite. `forge validate`/`forge doctor` clean.
The Specification-level Success Criteria (CHG-0045's PR #36 no longer
blocked by MR-015/MR-017) is directly confirmed by reproduction against
the real commits. Ready for Strict Review.
