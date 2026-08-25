---
forge:
  artifact: tasks
  schema: 1
change: CHG-0048
status: active
---
# Tasks — CHG-0048

- [ ] T-001 RED: write TDD-001–009 against `_validate_review_profile_floor` (not yet created) and the four not-yet-modified Schemas (Plan item 1).
- [ ] T-002 GREEN: add `_PROFILE_RANK`/`_validate_review_profile_floor` to `validation/__init__.py`; wire it into `validate_project`'s existing `resolve_effective_flow` call (Plan item 2).
- [ ] T-003 GREEN: edit the four Schemas (`change-v2`, `policy-review-v2`, `project-flow` additive; `flow` const→boolean + required `profile`); confirm `policy-review.schema.json` (Protocol 1) untouched (Plan item 3).
- [ ] T-004 Edit `fast.yml`/`standard.yml`/`full.yml`/`protocol/versions/2/policies/review.yml` with canonical `profile` values (Plan item 4).
- [ ] T-005 Edit `protocol/versions/2/contract/engineering.md`'s C-022/C-023 (replace) and C-031 (clarify); confirm Protocol 1 Contract untouched (Plan item 5).
- [ ] T-006 RED: write TDD-010–012 against the current fixed review-instruction line (Plan item 6).
- [ ] T-007 GREEN: add `_REVIEW_PROFILE_INSTRUCTION` and index `_gate_instructions()` by it in both Adapters; confirm `review_independence.py` untouched (Plan item 6).
- [ ] T-008 RED: write TDD-013 against the current `MR-004` label (Plan item 7).
- [ ] T-009 GREEN: rename `MR-004`'s label in `merge_readiness/evaluator.py`; confirm trigger condition unchanged (Plan item 7).
- [ ] T-010 RED then GREEN: write and satisfy TDD-014 against the item 6/7 implementation — a property proof, not new behavior (Plan item 8).
- [ ] T-011 RED then GREEN: write and satisfy TDD-015 against the current repository's historical Change population (Plan item 9).
- [ ] T-012 Add `protocol/compatibility.md` entry and `CHANGELOG.md` entry (Plan item 10).
- [ ] T-013 Full suite, `forge validate`, and final diff-scope confirmation (Plan item 11).

## Status

No task has started.
