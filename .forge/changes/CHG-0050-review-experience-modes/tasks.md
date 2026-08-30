---
forge:
  artifact: tasks
  schema: 1
change: CHG-0050
status: active
---
# Tasks — CHG-0050

- [ ] T-001 Extract `compute_review_profile_floor`; refactor `_validate_review_profile_floor` to use it (Plan item 1, TDD-001).
- [ ] T-002 Add `resolve_effective_review_profile(floor, mode)` to `protocol_resolution/__init__.py` (Plan item 2, TDD-002, TDD-003).
- [ ] T-003 Add `review.mode`/`review.current_phase` to `change-v2.schema.json` (Plan item 3, TDD-004, TDD-008).
- [ ] T-004 Add `_validate_review_current_phase`, wire into `validate_project` (Plan item 4, TDD-006, TDD-007).
- [ ] T-005 Add `review.preferred_mode` to `project.schema.json` (Plan item 5).
- [ ] T-006 `_manifest()` gains `review_mode` parameter (Plan item 6, TDD-010).
- [ ] T-007 `forge change new` reads `review.preferred_mode` (Plan item 7, TDD-009, TDD-010, TDD-011).
- [ ] T-008 Create `adapters/review_experience.py` (Plan item 8).
- [ ] T-009 Update both Adapters' `_gate_instructions` (Plan item 9, TDD-012).
- [ ] T-010 Add `forge change review-status` (Plan item 10, TDD-013, TDD-014).
- [ ] T-011 Update `protocol/compatibility.md` and `CHANGELOG.md` (Plan item 11).

## Status

Not started. Plan approved (DEC-003, human, 2026-08-30). Implementation begins at T-001.
