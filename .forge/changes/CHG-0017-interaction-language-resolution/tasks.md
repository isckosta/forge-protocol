---
forge:
  artifact: tasks
  schema: 1
change: CHG-0017
status: ready
---
# Tasks — CHG-0017

- [ ] T-001 Add `interaction.language` to `protocol/schemas/project.schema.json`.
- [ ] T-002 Add `C-070`–`C-073` to `protocol/contract/engineering.md` and
      `protocol/versions/2/contract/engineering.md`.
- [ ] T-003 Add `§42` ("Interaction Language Resolution") to
      `protocol/specification.md`.
- [ ] T-004 Write `docs/adr/0015-interaction-language-resolution.md`
      (number re-verified against `docs/adr/` immediately before writing).
- [ ] T-005 RED: write TDD-001 tests against the not-yet-existing
      `interaction_language` field/rendering in
      `src/forge_cli/adapters/codex/projection.py`; execute; confirm
      failure for the expected reason.
- [ ] T-006 GREEN: implement `AdapterProjectionContext.interaction_language`,
      `CodexProjectionInput.interaction_language`, `_skill_content(...)`
      rendering, and the `service.py` population at both construction
      sites.
- [ ] T-007 Refactor as needed; TDD-001 remains GREEN throughout (C-014).
- [ ] T-008 `pytest -q`, `forge validate`, `forge doctor` — record exact
      results against the pre-Implementation baseline (TDD-002).
- [ ] T-009 `CHANGELOG.md` entry, `ROADMAP.md` status flip,
      `knowledge-capture.md`, `traceability.yml`, `tdd-evidence.yml` (all
      produced from real Implementation evidence, not drafted ahead of
      it — `plan.md` step 6).
- [ ] T-010 Freeze Implementation subject, record provenance.
- [ ] T-011 Independent Strict Review Iteration 1 (separate Execution/
      Context).
- [ ] T-012 Resolution (if any Findings require one) + Resolution
      provenance.
- [ ] T-013 Independent Resolution Verification (if T-012 ran) — separate
      Execution/Context again.
- [ ] T-014 Completion: all FULL Gates satisfied.

## Status

Ready. Implementation not started.
