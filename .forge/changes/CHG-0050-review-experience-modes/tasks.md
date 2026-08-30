---
forge:
  artifact: tasks
  schema: 1
change: CHG-0050
status: complete
---
# Tasks — CHG-0050

- [x] T-001 Extract `compute_review_profile_floor`; refactor `_validate_review_profile_floor` to use it (Plan item 1, TDD-001).
- [x] T-002 Add `resolve_effective_review_profile(floor, mode)` to `protocol_resolution/__init__.py` (Plan item 2, TDD-002).
- [x] T-003 Add `review.mode`/`review.current_phase` to `change-v2.schema.json` (Plan item 3, TDD-003).
- [x] T-004 Add `_validate_review_current_phase`, wire into `validate_project` (Plan item 4, TDD-004).
- [x] T-005 Add `review.preferred_mode` to `project.schema.json` (Plan item 5, TDD-005).
- [x] T-006 `_manifest()` gains `review_mode` parameter (Plan item 6, TDD-006).
- [x] T-007 `forge change new` reads `review.preferred_mode` (Plan item 7, TDD-007).
- [x] T-008 Create `adapters/review_experience.py` (Plan item 8, TDD-008/TDD-009).
- [x] T-009 Update both Adapters' `_gate_instructions` (Plan item 9, TDD-008/TDD-009; corrected per DEC-004).
- [x] T-010 Add `forge change review-status` (Plan item 10, TDD-010).
- [x] T-011 Update `protocol/compatibility.md` and `CHANGELOG.md` (Plan item 11).

## Status

Complete. All 11 Plan items implemented with RED-before-GREEN TDD (10 cycles, `tdd-evidence.yml`). Full suite: 856 passed. `forge validate`: PASS. DEC-004 recorded a non-material, Implementation-time correction to T-009's mechanism (Adapter projection is per-Flow, not per-Change). Ready for Verification and independent Strict Review.
