---
forge:
  artifact: tasks
  schema: 1
change: CHG-0013
status: ready
---
# Tasks — CHG-0013

- [x] T-001 Add `decisions` array to `change.schema.json` and
      `change-v2.schema.json`.
- [x] T-002 Add `protocol/schemas/policy-decision.schema.json`; register
      `forge/policy/decision@1` in `catalog.yml`.
- [x] T-003 Add C-051–C-059 to `protocol/contract/engineering.md`.
- [x] T-004 Backfill C-047–C-050 and add C-051–C-059 to
      `protocol/versions/2/contract/engineering.md`.
- [x] T-005 Add §39 to `protocol/specification.md`.
- [x] T-006 Add `protocol/policies/decision.yml`.
- [x] T-007 Add compatibility subsection to `protocol/compatibility.md`.
- [x] T-008 Add one sentence to `ARCHITECTURE.md` §17.
- [x] T-009 RED: reconstructed (implementation was drafted first — see
      `verification.md`); wiring temporarily removed, 8/14 tests failed for
      the expected reason, wiring restored.
- [x] T-010 GREEN: `_validate_unresolved_decisions`, wired into
      `validate_project` for every protocol id.
- [x] T-011 TDD-002 through TDD-012 per Test Strategy (14 tests total).
- [x] T-012 `pytest -q` (389 passed), `forge validate` ("Forge project is
      valid," matching the clean-`main` baseline), `forge doctor` (all PASS).
- [x] T-013 `docs/adr/0012-unresolved-decision-management.md`,
      `knowledge-capture.md`, `traceability.yml`, `tdd-evidence.yml`; RFC
      requirement evaluated (not required — see ADR-0012/knowledge-capture.md).
- [ ] T-014 Freeze this Change's own Implementation subject; record
      `implementation`-role provenance.
- [ ] T-015 Independent Strict Review Iteration 1 (`kind: initial_review`,
      separate Execution/Context).
- [ ] T-016 Resolution of any blocking Findings, re-review, Completion —
      only after independent PASS and all FULL Completion Gates.

## Status

T-001 through T-013 complete. T-014 (freeze/provenance) is next, followed by
an independent Strict Review Iteration in a separate Execution/Context from
this Implementation session — never this same session.
