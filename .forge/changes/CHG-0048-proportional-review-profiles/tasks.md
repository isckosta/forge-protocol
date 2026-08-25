---
forge:
  artifact: tasks
  schema: 1
change: CHG-0048
status: complete
---
# Tasks — CHG-0048

- [x] T-001 RED/T-002 GREEN: actual sequencing swapped with T-003/T-004 (documented discovery, `tdd-evidence.yml` TDD-002 notes, C-069) — `_PROFILE_RANK`/`_validate_review_profile_floor` added to `validation/__init__.py`, wired into `validate_project`'s existing `resolve_effective_flow` call; `tests/unit/test_validation_review_profile.py` (Plan items 1-2).
- [x] T-003 The four Schemas edited (`change-v2` — `review.iterations[].profile`, `policy-review-v2`, `project-flow` additive; `flow` const→boolean + required `profile`); `policy-review.schema.json` (Protocol 1) confirmed untouched (Plan item 3).
- [x] T-004 `fast.yml`/`standard.yml`/`full.yml`/`protocol/versions/2/policies/review.yml` carry canonical `profile` values (Plan item 4).
- [x] T-005 `protocol/versions/2/contract/engineering.md`'s C-022/C-023 replaced, C-031 clarified; Protocol 1 Contract confirmed untouched (Plan item 5).
- [x] T-006/T-007 `REVIEW_PROFILE_INSTRUCTION` added to the shared `review_independence.py` (implementation-time refinement over the original Plan wording, disclosed in `verification.md`), indexed by both Adapters' `_gate_instructions()`; independence block confirmed byte-unchanged; `tests/unit/test_{claude_code,codex}_projection_gates.py` (Plan item 6).
- [x] T-008/T-009 RED (with a self-caught case-sensitivity assertion bug, then genuine RED) then GREEN: `MR-004` label renamed in `merge_readiness/evaluator.py`; trigger condition unchanged (Plan item 7).
- [x] T-010 TDD-014 written and GREEN on first run — property proof, not new behavior (Plan item 8).
- [x] T-011 TDD-015 written and GREEN on first run (Plan item 9).
- [x] T-012 `protocol/compatibility.md` and `CHANGELOG.md` entries added (Plan item 10).
- [x] T-013 Full suite (784 passed), `forge validate` (PASS), diff-scope confirmed exactly 33 files, no premature abstraction (Plan item 11).

## Status

All tasks complete. Independent Strict Review pending.
