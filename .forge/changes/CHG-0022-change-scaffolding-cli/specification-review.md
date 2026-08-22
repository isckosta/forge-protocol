---
forge:
  artifact: specification_review
  schema: 1
change: CHG-0022
status: passed
---

# Specification Review — Change Scaffolding CLI

## Verdict

**PASS.** Multiple independent cold review passes found and resolved the
documented findings; the final pass found no blocking contradiction. The
Specification Review Gate is satisfied.

## Findings

### SR-001 — BLOCKER — Initial TDD evidence status was schema-invalid

The first Specification required `tdd-evidence.yml` with `status: pending`,
but `protocol/schemas/tdd-evidence.schema.json` permits `active`, `compliant`,
`complete`, `not_applicable`, and `exception`, not `pending`.

**Resolution:** The initial TDD evidence state is now `active` with
`cycle_count: 0` and `cycles: []`; `manifest.yml` retains its separately
valid `tdd.status: pending` lifecycle state. TDD-002 and the artifact table
were updated to test this distinction.

### SR-002 — MAJOR — FAST had no defined scaffold

FR-003 accepted any configured Flow while FR-004 specified only STANDARD and
FULL, leaving FAST's `inspection` and `documentation_impact` semantics
undefined.

**Resolution:** FR-004 and TDD-002 now define and test FAST's exact artifact
set. The intent, discovery, acceptance criteria, and plan explicitly cover
FAST, STANDARD, and FULL.

### SR-003 — MAJOR — Failure atomicity lacked a mechanism

The first Plan required no partial target after a write failure but did not
specify how to achieve it.

**Resolution:** FR-007, TDD-005, and Plan items 1/3/4 now require rendering in
memory, exclusive final-directory creation, exclusive `x`-mode file writes,
and cleanup of only files owned by the invocation on failure.

### SR-004 — MAJOR — Collision behavior was under-specified

Because numbering advances past existing directories, an ordinary existing
Change is not a collision; only a destination appearing after planning can
exercise collision behavior.

**Resolution:** FR-007 and TDD-005 define preflight and publication-time
collision checks and state that existing Changes are skipped by allocation;
the test targets a destination that appears between planning and publication.

### SR-005 — MAJOR — Initial scaffold and later evidence artifacts were mixed

The first Plan assembled `traceability.yml` and `provenance.yml` even though
FR-004 omitted them and an empty traceability placeholder would violate its
`minItems: 1` task constraint.

**Resolution:** FR-004 explicitly separates initial scaffold artifacts from
later lifecycle evidence. `traceability.yml`, `provenance.yml`, and final
review-control metadata are not generated as empty placeholders.

### SR-006 — MINOR — Wheel test path was inaccurate

The first Plan named `tests/integration/adapter_distribution.py`, but the
repository file is `tests/integration/test_adapter_distribution.py`.

**Resolution:** Plan item 6 now names the actual distribution test and
`adapter_cli_wheel_probe.py` helper.

### SR-007 — MINOR — Slug boundaries were incomplete

The first wording did not say whether consecutive hyphens or Unicode letters
were accepted.

**Resolution:** FR-002 now gives the exact ASCII regex
`^[a-z0-9]+(?:-[a-z0-9]+)*$`, and TDD-001 lists all boundary cases.

## Checked and found sound

- STANDARD classification is independently defensible: FAST is disqualified
  by `significant_cross_module_change`, while no FULL-only semantic surface
  is introduced.
- The CLI registration pattern follows `app.add_typer(adapter_app,
  name="adapter")` without expanding the lifecycle execution boundary.
- `review.iteration: 0` and `iterations: []` match the pending manifest
  precedent and the active `forge/change@2` schema.
- The scope excludes schema changes and roadmap items #3–#10.

## Resolution Applied

The seven findings above were resolved in the same authoring session. The
corrected Specification, Test Design, and Plan are the artifacts reviewed by
the second cold pass.

## Second Review Record

The second independent cold review found five MAJOR findings:

- FAST's conditional `test_design` stage was not specified.
- Exclusive no-replace publication and its failure behavior were not concrete.
- Publication-time collision testing had no deterministic race seam.
- Plan-before-mutation ordering was not observable in the proposed test.
- This artifact's own status contradicted its pending second review.

The corrective edits are now recorded in `specification.md` and
`test-design.md`. A third cold review must verify them before Implementation.

The third independent cold review found seven further findings: conditional
Flow behavior still lacked a complete truth table; the error contract was not
exact for every failure class; the mutation-order test did not snapshot
temporary siblings; rollback lacked an injected file-N failure case; manifest
markers for non-file stages were underspecified; title humanization was not
algorithmically fixed; and plan-line ordering was not explicit. These findings
are being resolved in the next document revision.

The fourth independent cold review then found three MAJOR findings and one
MINOR: publication/rollback codes were incomplete; missing/malformed/disabled
Flow cases were not individually mapped; and no-mutation tests did not compare
pre-existing bytes for all failure classes. Those findings are resolved by
the explicit error matrix and byte-snapshot requirements now present in
`specification.md` and `test-design.md`. A fifth cold pass is required to
confirm the final state.

The fifth independent cold review found three MAJOR findings and two MINOR:
the rollback-incomplete code contradicted itself, FULL ordering placed
`tasks` before `plan`, conditional predicates were not linked, the unknown
canonical Flow test was absent, and the no-mutation snapshot was too narrow.
These are resolved by the final error table, Flow truth-table rule, corrected
FULL order, explicit test case, and full non-Git workspace byte snapshot.
A sixth cold pass is required for final approval.

The sixth and seventh cold reviews additionally found stale publication prose
in this Review artifact, grouped error rows, and incomplete explicit snapshot
coverage for invalid slug, packaged-resource, and rollback-incomplete cases.
Those records are now corrected: this artifact describes exclusive mkdir/x-
mode publication, the Specification assigns one code per failure class, and
the Test Design requires the full workspace byte snapshot for every listed
failure class. A fresh cold pass is required to close the Gate.

## Conclusion

The first through seventh review findings are resolved in the documents. The
final independent cold pass recorded PASS: FULL excludes `test_design`,
publication uses exclusive directory/file creation without overwrite,
failure codes are distinct including rollback-incomplete, enabled Flow
validation is explicit, stage order and conditional truth tables are
canonical, snapshots cover all failure classes, and manifest/scope semantics
are coherent. Implementation may now begin under the approved Plan.
