---
forge:
  artifact: tasks
  schema: 1
change: CHG-0011
status: active
---
# Tasks — CHG-0011

- [x] T-001 Extend `change-v2.schema.json` (iteration kind/escalation/
      convergence fields, top-level `review.convergence`).
- [x] T-002 Extend `execution-provenance.schema.json` (`scope`, `targets`).
- [x] T-003 Add C-047–C-050 to `protocol/contract/engineering.md`.
- [x] T-004 Add §10–§13 to `protocol/versions/2/specification.md`.
- [x] T-005 Add `resolution_verification` block to
      `protocol/versions/2/policies/review.yml`.
- [x] T-006 Add compatibility subsection to `protocol/compatibility.md`.
- [x] T-007 Add `review.convergence.allow_residual_risk_acceptance` to
      `.forge/forge.yml` (default `false`, explicit) and confirm
      `load_project_configuration`/`project.schema.json` accept it.
- [x] T-008 RED: TDD-012 (legacy-manifest regression) against not-yet-written
      `_validate_resolution_verification`.
- [x] T-009 GREEN: `_resolution_delta` + `_validate_resolution_verification`,
      wired only when a manifest has any `kind`-classified Iteration.
- [x] T-010 TDD-013, 014, 016, 018, 020 (subset) per Test Strategy; two real
      defects found and fixed via RED->GREEN during this task (see
      `verification.md`).
- [x] T-011 Run full `pytest -q` (242 passed), `forge validate` (one
      pre-existing, out-of-scope finding unchanged from clean `main`),
      `forge doctor` (all PASS).
- [x] T-012 `docs/adr/0011-review-convergence-boundary.md`,
      `knowledge-capture.md`, `traceability.yml`, `tdd-evidence.yml`.
- [x] T-013 Freeze this Change's own Implementation subject; record
      `implementation`-role provenance (`implementation-001`, superseded by
      `implementation-002` after a pre-freeze-discipline correction).
- [x] T-014 Independent Strict Review Iteration 1 (`kind: initial_review`,
      separate Execution/Context) — REQUEST CHANGES: 1 BLOCKER
      (CHG-0011-R001), 2 MAJOR (R002, R003), 1 MINOR (R004), 1 OBSERVATION
      (R005). See `review.md`.
- [x] T-017 Resolution 1: fix R001 (`convergence_decision` moved to
      per-Iteration `iterations[i+1]`, checked at every historical episode
      index, not a manifest-wide field), R002 (retract contradictory AC-009),
      R003 (remove `fnmatch`, exact-path-only scope), R004 (correct
      Specification's overstated enforcement claim), R005 (accepted as
      documented, intentional scope narrowing). `specification-drift.md`
      records the Requirement-level corrections (R001-R003 are genuine
      Specification defects, not implementation-only fixes).
- [ ] T-015 Declare Resolution scope/targets, freeze, then independent
      `resolution_verification` — dogfooding the mechanism this Change
      itself introduces on its own second review cycle.
- [ ] T-016 Complete only after independent PASS and all FULL Completion
      Gates.
