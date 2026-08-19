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
- [x] T-008 **Not performed.** DEC-001 resolved as Alternative A
      (human, 2026-08-19): no `## Result`/`## Verdict` heading-presence
      Core validation check is built. Retained here, struck through in
      spirit, as the recorded reason this task does not exist rather
      than a silently dropped one.
- [x] T-009 Refactor as needed; TDD-001/TDD-002 (and TDD-008 if
      applicable) remain GREEN throughout (C-014).
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
- [x] T-013 Freeze Implementation subject; record provenance.
- [ ] T-014 Independent Strict Review (`kind: initial_review`, separate
      Execution/Context from Implementation).
- [ ] T-015 Resolve any blocking Findings; independent Resolution
      Verification if needed (separate Execution/Context again).
- [ ] T-016 Completion: verify every FULL Gate satisfied (Verification
      passed, Review passed, Documentation Impact evaluated and updated,
      Knowledge Capture complete, no unresolved BLOCKER Findings).

## Status

T-001 through T-013 complete, including `verification.md` (PASS) and
`provenance.yml` (Implementation subject frozen at commit `e50d3c5`).
T-014 onward requires a distinct Execution and Execution Context per
Protocol 2 (Reviewer/Resolver independence,
`protocol/versions/2/specification.md` §2) — this session cannot perform
Strict Review on its own Implementation without constituting self-review,
and does not attempt to. Subsequent commits are restricted to
Change-local review-control metadata (this file, `manifest.yml`,
`provenance.yml`, `review.md`), per the same freeze discipline
`CHG-0015` established.
