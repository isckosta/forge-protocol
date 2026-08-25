---
forge:
  artifact: tasks
  schema: 1
change: CHG-0046
status: pending
---

# CHG-0046 · Tasks

> Execution Checklist

## Overview
| | |
|---|---|
| **Change** | CHG-0046 |
| **Flow** | FULL |
| **Status** | Ready |

## Execution

### Plan 1-3 · MR-015 TDD tests (RED)

- [ ] T-001 Add TDD-001 (`state.current: complete`, Change-local post-freeze
      file tolerated), confirm RED for the expected reason (`MR-015` in
      stdout).
      `Plan: 1` · `Requirements: FR-001` · `Test Design: TDD-001`
- [ ] T-002 Add TDD-002 (same file, `state.current` not `complete`),
      confirm it passes against unmodified `evaluator.py` (guard, not RED).
      `Plan: 2` · `Requirements: FR-001` · `Test Design: TDD-002`
- [ ] T-003 Add TDD-003 (characterization test: `change_root`-external
      file post-freeze while complete; documents today's actual `MERGE
      READY` outcome).
      `Plan: 3` · `Requirements: (none — Out of Scope characterization)` · `Test Design: TDD-003`

### Plan 4 · MR-015 implementation (GREEN)

- [ ] T-004 Implement the state-conditioned allowed-set change in
      `evaluator.py`'s `_check_change()` per Architecture's Design section.
      Confirm TDD-001 GREEN; TDD-002/TDD-003 unaffected.
      `Plan: 4` · `Requirements: FR-001` · `Test Design: TDD-001, TDD-002, TDD-003`

### Plan 5-6 · MR-017 TDD tests and policy data (RED/GREEN)

- [ ] T-005 Add TDD-004 (ten paths, parametrized), confirm RED
      (`ambiguous` today).
      `Plan: 5` · `Requirements: FR-002` · `Test Design: TDD-004`
- [ ] T-006 Add the four prefix/path entries to
      `protocol/policies/merge-readiness.yml`. Confirm TDD-004 GREEN.
      `Plan: 6` · `Requirements: FR-002` · `Test Design: TDD-004`

### Plan 7-9 · Regression and acceptance verification

- [ ] T-007 Confirm `test_ambiguous_unclassified_diff_is_blocked` and the
      full existing `tests/cli/test_merge_check.py` suite pass unmodified
      (AC-005 / TDD-005).
      `Plan: 7` · `Requirements: FR-002`
- [ ] T-008 Run full `pytest -q`, `forge validate`, `forge doctor` against
      this repository's own state; confirm clean.
      `Plan: 8`
- [ ] T-009 Reproduce CHG-0045's actual PR #36 base/head against this
      Change's implementation; confirm `MR-015`/`MR-017` absent, record
      before/after output.
      `Plan: 9` · `Requirements: FR-001, FR-002`

### Plan 10-13 · Evidence and completion

- [ ] T-010 Write `verification.md` with real evidence for every TDD-xxx,
      full command output, and item 9's reproduction.
      `Plan: 10`
- [ ] T-011 Documentation Impact evaluation (`CHANGELOG.md`, possible ADR
      for DEC-001).
      `Plan: 11`
- [ ] T-012 `knowledge-capture.md` from real Implementation/Review
      evidence.
      `Plan: 12`
- [ ] T-013 Independent Strict Review of the frozen subject.
      `Plan: 13`

## Status

No task has started. Blocked on the C-077 Plan Decision (explicit human
authorization) before any task above may begin — see `plan.md`
"Implementation Boundary".
