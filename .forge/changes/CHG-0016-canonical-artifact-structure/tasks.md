---
forge:
  artifact: tasks
  schema: 1
change: CHG-0016
status: ready
---
# Tasks — CHG-0016

- [x] T-001 Write `protocol/artifact-structure.md` (Principles + per-type
      structural guidance for all fourteen real Artifact types), per
      `architecture.md`'s Content Shape section.
- [x] T-002 Add `C-067` onward to `protocol/contract/engineering.md`,
      wording governed by DEC-001's resolution.
- [x] T-003 Add `§41` ("Canonical Artifact Structure") to
      `protocol/specification.md`.
- [x] T-004 Add a "Canonical Artifact Structure (CHG-0016)" addendum to
      `protocol/compatibility.md`, wording governed by DEC-001's
      resolution.
- [x] T-005 Add one sentence to `ARCHITECTURE.md` §5.
- [x] T-006 RED: write TDD-001/TDD-002 against the not-yet-existing
      `artifact_structure_content` field in
      `src/forge_cli/adapters/codex/projection.py`; execute; confirm
      failure for the expected reason (field/resource absent), not an
      environment failure.
- [x] T-007 GREEN: implement the resource load and bundle field in
      `projection.py`.
- [ ] ~~T-008~~ **Not performed, by design.** DEC-001 resolved as
      Alternative A (human, 2026-08-19): no `## Result`/`## Verdict`
      heading-presence Core validation check is built. Left unchecked
      (Strict Review R011: a checked box is a scanable "done" signal
      this task does not have) with the reason recorded, rather than
      silently removed from the list.
- [x] T-009 Refactor as needed; TDD-001/TDD-002/TDD-003 remain GREEN
      throughout (C-014).
- [x] T-010 `pytest -q`, `forge validate`, `forge doctor` — record exact
      results against the pre-Implementation baseline captured in
      `plan.md` step 5 (TDD-003).
- [x] T-011 New `examples/canonical-artifacts/verification.md` and
      `examples/canonical-artifacts/review.md`, annotated per
      `architecture.md`'s Canonical Examples section.
- [x] T-012 `docs/adr/0014-canonical-artifact-structure.md` (number
      re-verified against `docs/adr/` immediately before writing, not
      assumed); `CHANGELOG.md` entry; `knowledge-capture.md`;
      `traceability.yml`; `tdd-evidence.yml` (all produced from real
      Implementation evidence, not drafted ahead of it — `plan.md` step 7).
- [x] T-013 Froze Implementation subject (`implementation-001`, `e50d3c5`).
- [x] T-014 Independent Strict Review Iteration 1 (`kind: initial_review`,
      separate Execution/Context) — REQUEST CHANGES: 1 BLOCKER (R012,
      latent defect inherited from `CHG-0015`), 2 MAJOR (R001, R002),
      6 MINOR (R003–R008), 3 OBSERVATION (R009–R011).
- [x] T-015 Resolution (`resolution-001`, `848adc9`, same session as
      Implementation — only Reviewer independence is required by C-026)
      addressed R001–R008, R010–R012 with declared `scope`/`targets`;
      R009 needed no fix. Independent Resolution Verification (Iteration 2,
      separate Execution/Context again) — PASS, `full_review_required:
      false`, `new_material_findings: 0`, two new non-blocking OBSERVATION
      (R013, R014, deferred). See `review.md`.
- [x] T-016 Completion: all FULL Gates satisfied (Verification passed,
      Review passed, Documentation Impact evaluated and updated, Knowledge
      Capture complete, no unresolved BLOCKER Findings).

## Status

All tasks complete. `manifest.yml` `state.current: complete`.
