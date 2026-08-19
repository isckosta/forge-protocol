---
forge:
  artifact: tasks
  schema: 1
change: CHG-0017
status: complete
---
# Tasks — CHG-0017

- [x] T-001 Add `interaction.language` to `protocol/schemas/project.schema.json`.
- [x] T-002 Add `C-070`–`C-073` to `protocol/contract/engineering.md` and
      `protocol/versions/2/contract/engineering.md`.
- [x] T-003 Add `§42` ("Interaction Language Resolution") to
      `protocol/specification.md`.
- [x] T-004 Write `docs/adr/0015-interaction-language-resolution.md`
      (number re-verified against `docs/adr/` immediately before writing).
- [x] T-005 RED: write TDD-001 tests against the not-yet-existing
      `interaction_language` field/rendering in
      `src/forge_cli/adapters/codex/projection.py`; execute; confirm
      failure for the expected reason.
- [x] T-006 GREEN: implement `AdapterProjectionContext.interaction_language`,
      `CodexProjectionInput.interaction_language`, `_skill_content(...)`
      rendering, and the `service.py` population at both construction
      sites.
- [x] T-007 Refactor as needed; TDD-001 remains GREEN throughout (C-014).
- [x] T-008 `pytest -q`, `forge validate`, `forge doctor` — record exact
      results against the pre-Implementation baseline (TDD-002).
- [x] T-009 `CHANGELOG.md` entry, `ROADMAP.md` status flip,
      `knowledge-capture.md`, `traceability.yml`, `tdd-evidence.yml` (all
      produced from real Implementation evidence, not drafted ahead of
      it — `plan.md` step 6).
- [x] T-010 Freeze Implementation subject, record provenance.
- [x] T-011 Independent Strict Review Iteration 1 (separate Execution/
      Context).
- [x] T-012 Resolution (if any Findings require one) + Resolution
      provenance.
- [ ] ~~T-013~~ **Not performed, by design.** Both Findings T-012's
      Resolution addressed (R001, R002) were MINOR, non-blocking per
      `protocol/policies/review.yml`, and `review_passed` was already
      achieved on Iteration 1 before the Resolution existed — unlike
      `CHG-0016`, which required Review 2 to reach `review_passed` at all.
      Left unchecked with the reason recorded, matching `CHG-0016/tasks.md`
      T-008's own convention for a task not performed by design.
- [x] T-014 Completion: all FULL Gates satisfied (Verification passed,
      Review passed with 0 BLOCKER/MAJOR, Resolution of both non-blocking
      MINOR Findings recorded, Documentation Impact evaluated and updated,
      Knowledge Capture complete).

## Status

All tasks complete or explicitly not performed by design (T-013).
`manifest.yml` `state.current: complete`.
