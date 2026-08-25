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

- [x] T-001 Add TDD-001 (`state.current: complete`, Change-local post-freeze
      file tolerated), confirm RED for the expected reason (`MR-015` in
      stdout).
      `Plan: 1` · `Requirements: FR-001` · `Test Design: TDD-001`
- [x] T-002 Add TDD-002 (same file, `state.current` not `complete`),
      confirm it passes against unmodified `evaluator.py` (guard, not RED).
      `Plan: 2` · `Requirements: FR-001` · `Test Design: TDD-002`
- [x] T-003 Add TDD-003 (characterization test: `change_root`-external
      file post-freeze while complete; documents today's actual `MERGE
      READY` outcome).
      `Plan: 3` · `Requirements: (none — Out of Scope characterization)` · `Test Design: TDD-003`

### Plan 4 · MR-015 implementation (GREEN)

- [x] T-004 Implement the state-conditioned allowed-set change in
      `evaluator.py`'s `_check_change()` per Architecture's Design section.
      Confirm TDD-001 GREEN; TDD-002/TDD-003 unaffected.
      `Plan: 4` · `Requirements: FR-001` · `Test Design: TDD-001, TDD-002, TDD-003`

### Plan 5-6 · MR-017 TDD tests and policy data (RED/GREEN)

- [x] T-005 Add TDD-004 (ten paths, parametrized), confirm RED
      (`ambiguous` today).
      `Plan: 5` · `Requirements: FR-002` · `Test Design: TDD-004`
- [x] T-006 Add the four prefix/path entries to
      `protocol/policies/merge-readiness.yml`. Confirm TDD-004 GREEN.
      `Plan: 6` · `Requirements: FR-002` · `Test Design: TDD-004`

### Plan 7-9 · Regression and acceptance verification

- [x] T-007 Confirm `test_ambiguous_unclassified_diff_is_blocked` and the
      full existing `tests/cli/test_merge_check.py` suite pass unmodified
      (AC-005 / TDD-005).
      `Plan: 7` · `Requirements: FR-002`
- [x] T-008 Run full `pytest -q`, `forge validate`, `forge doctor` against
      this repository's own state; confirm clean.
      `Plan: 8`
- [x] T-009 Reproduce CHG-0045's actual PR #36 base/head against this
      Change's implementation; confirm `MR-015`/`MR-017` absent, record
      before/after output.
      `Plan: 9` · `Requirements: FR-001, FR-002`

### Plan 10-13 · Evidence and completion

- [x] T-010 Write `verification.md` with real evidence for every TDD-xxx,
      full command output, and item 9's reproduction.
      `Plan: 10`
- [x] T-011 Documentation Impact evaluation (`CHANGELOG.md`, possible ADR
      for DEC-001). Superseded/completed by T-018 below (Iteration
      1's findings pushed this later in sequence).
      `Plan: 11`
- [x] T-012 `knowledge-capture.md` from real Implementation/Review
      evidence. Superseded/completed by T-019 below.
      `Plan: 12`
- [x] T-013 Independent Strict Review of the frozen subject
      (`60b699bb69c06ed0b078572dd705191e73441c68`), Iteration 1
      (`review-001`): **REQUEST CHANGES** — 0 BLOCKER, 2 MAJOR (R001, R002),
      0 MINOR, 1 OBSERVATION (R003, non-blocking). Both MAJORs
      independently reproduced by the Reviewer, both real: R001, an
      unguarded `manifest.get("state", {}).get("current")` read in the new
      `is_complete` line crashes with `AttributeError` on a malformed
      `state:` field instead of degrading gracefully, inconsistent with
      the file's own established guarded-read convention; R002, the
      `.forge/adapters/` `material_prefixes` entry is broader than
      Architecture's own stated `.forge/adapters/*/installation.yml`
      design and Specification's AC-005 boundary, silently reclassifying
      sibling adapter-directory files (e.g. `config.yml`) from `ambiguous`
      to `material`. Full findings: `review.md`.
      `Plan: 13`
- [x] T-014 Resolution of R001: hoisted the file's existing
      isinstance-guarded `state` read to the top of `_check_change()` and
      reused it for `is_complete`, removing the second, unguarded inline
      read entirely. Added TDD-006, confirmed RED against the reviewed
      subject (`60b699b`, re-reproducing R001 exactly) before re-applying
      the fix, then GREEN.
      `Requirements: FR-001` · `Test Design: TDD-006`
- [x] T-015 Resolution of R002: replaced the `.forge/adapters/`
      `material_prefixes` entry with two exact `material_paths` entries
      (`.forge/adapters/claude-code/installation.yml`,
      `.forge/adapters/codex/installation.yml`), matching Architecture's
      own stated design exactly. Added TDD-007 (a sibling
      `.forge/adapters/claude-code/config.yml` path stays `ambiguous`),
      confirmed RED against the reviewed subject before the fix, then
      GREEN.
      `Requirements: FR-002` · `Test Design: TDD-007`
- [x] T-016 Post-Resolution housekeeping: while isolating TDD-006's
      fixture to evaluator.py's own code path, discovered a second,
      unrelated, pre-existing bug with the identical unguarded-string-state
      shape in `src/forge_cli/validation/__init__.py:321`
      (`st=m.get("state")or{}`), confirmed genuinely untouched by this
      Change's diff and out of Scope. Flagged separately (not fixed here,
      not silently ignored) — recorded in `verification.md`,
      `discovery.md` addendum, and as a standalone follow-up task.
- [x] T-017 Full suite (`pytest -q`, 704 passed), `forge validate`, `forge
      doctor` re-confirmed clean after the Resolution. Freeze the new
      Resolution subject; obtain an independent Resolution Verification
      (Iteration 2) of this Resolution.
      `Plan: 8`
- [x] T-018 Documentation Impact evaluation (`CHANGELOG.md`, possible ADR
      for DEC-001).
      `Plan: 11`
- [x] T-019 `knowledge-capture.md` from real Implementation/Review
      evidence, including the Resolution and the two out-of-scope findings
      surfaced along the way.
      `Plan: 12`

### Plan 14 · Specification Drift correction (post-Completion, pre-merge)

- [x] T-020 An external, independent reviewer (Codex, on PR #37) found
      DEC-001's `state.current`-keyed design directly contradicts
      Protocol 2 `specification.md` Sec 5/Sec 14. Wrote
      `specification-drift.md`; corrected `specification.md` (FR-001,
      CON-002, new CON-004, new AC-001/AC-003/AC-006/AC-007) and
      `architecture.md` (DEC-001 superseded, new DEC-003, revised Design
      section) to the explicit-anchored-scoped-renewal-record design.
      `Requirements: FR-001`
- [x] T-021 Reimplemented `evaluator.py`'s MR-015 check per the corrected
      design: renewal lookup against `role: implementation`/`resolution`
      records, ancestor-of-`head_revision` commit check, `scope`
      membership per uncovered path, anchored via the existing
      `_first_committed_record` (reused from MR-021, not reimplemented).
      Added TDD-008 through TDD-011 (AC-001/AC-003/AC-006/AC-007);
      TDD-001/TDD-002 kept, marked superseded, not deleted. Confirmed RED
      against the pre-Drift `evaluator.py` for each new test before
      implementing, then GREEN.
      `Requirements: FR-001` · `Test Design: TDD-008, TDD-009, TDD-010, TDD-011`
- [x] T-022 Re-verified the Specification-level acceptance check against
      CHG-0045's real PR #36 commits: `MR-015` now correctly fires again
      (CHG-0045's branch predates this correction and has no renewal
      record), a genuine, disclosed consequence of the fix being
      Protocol-conformant rather than a regression. Recorded in
      `verification.md`, not silently omitted.
      `Requirements: FR-001`
- [x] T-023 Full suite re-run (706 passed), `forge validate`/`forge
      doctor` clean. Updated `docs/adr/0018-...md` and `CHANGELOG.md`'s
      Unreleased entry to describe the corrected design, not the
      superseded one.
- [ ] T-024 Freeze the corrected implementation as a new Resolution
      subject; obtain a fresh independent Strict Review of the corrected
      design (the prior three Iterations reviewed DEC-001's now-superseded
      design, not DEC-003's).

## Status

T-001 through T-023 complete. T-024 (fresh independent Strict Review of
the corrected design) is next — required before Documentation
Impact/Knowledge Capture/Completion can be reconfirmed against the actual
shipped design.
