# Specification — End-to-End Examples (Curated Real Evidence)

## Summary

Two new curated READMEs (`strict-review-remediation` → `CHG-0016`,
`full-feature` → `CHG-0018`); two existing READMEs gain a short
cross-reference addendum; `examples/README.md` and `ROADMAP.md` updated.
No code, Contract, or schema change.

## Classification

**Flow: STANDARD.** See `discovery.md` "Flow Classification Finding".

## Functional Requirements

### FR-001 — `examples/strict-review-remediation/README.md`

A guided tour of `CHG-0016`'s real Iteration 1 (`REQUEST CHANGES`, 1
BLOCKER/2 MAJOR/6 MINOR/3 OBSERVATION) → Resolution (`848adc9`) →
Iteration 2 (`PASS`) cycle, citing real commit hashes and quoting real
Finding text (R012, R001, R002 at minimum), pointing a reader at
`.forge/changes/CHG-0016-canonical-artifact-structure/review.md` for the
full record rather than reproducing it wholesale.

### FR-002 — `examples/full-feature/README.md`

A guided tour of `CHG-0018`'s real FULL-flow evidence: the two Core-leak
fixes, the new Adapter, and the dogfooded Golden Path's real,
independently-executed bug-catch — citing real commit hashes, pointing
at `.forge/changes/CHG-0018-second-harness-adapter-claude-code/` for the
full record.

### FR-003 — Cross-references on existing examples

`golden-path-standard/README.md` and `golden-path-claude-code/README.md`
each gain a short addendum naming the additional ROADMAP category they
satisfy (`standard-feature`/`codex-adapter-project`, and `fast-bugfix`
respectively) — an addition, not a rewrite of their existing content.

### FR-004 — `examples/README.md`

Rewritten to map all five ROADMAP-named categories to their real
evidence directory, replacing the current aspirational "Future examples
should also demonstrate" list with what actually exists.

### FR-005 — `ROADMAP.md` status

A status line for "End-to-End Examples & External Project Validation"
naming what's satisfied (five categories, curated real evidence) and
what remains explicitly open (the External validation matrix — no real
non-Python/non-this-repository target exists to validate against).

## Constraints

### CON-001 — No fabricated evidence

Every commit hash, Finding ID, and quoted excerpt in any new or updated
README is checked against real `git show`/file content before Verification,
not reconstructed from memory of this conversation.

### CON-002 — No duplicated normative authority

The two existing golden-path READMEs are not rewritten wholesale; the
two new READMEs point at, rather than reproduce, `.forge/changes/CHG-0016.../`
and `.forge/changes/CHG-0018.../`'s full artifact sets (INV-001-style
reference-not-restate discipline).

### CON-003 — Historical validity

No historical Change's own artifacts are modified. `forge validate`/
`forge doctor`/`pytest -q` are unaffected (no code touched).

## Acceptance Criteria

- **AC-001**: `examples/strict-review-remediation/README.md` exists;
  every commit hash and Finding excerpt it cites matches real `git show`/
  `review.md` content exactly.
- **AC-002**: `examples/full-feature/README.md` exists; every commit hash
  and claim it cites matches real `git show`/artifact content exactly.
- **AC-003**: both existing golden-path READMEs gain their addendum,
  with no other content changed.
- **AC-004**: `examples/README.md` correctly maps all five ROADMAP
  categories.
- **AC-005**: `ROADMAP.md` reflects this Change; the External validation
  matrix is explicitly still named open, not silently dropped.
- **AC-006**: `pytest -q`/`forge validate`/`forge doctor` are unchanged
  (no code touched).

## Out of Scope

- The External validation matrix.
- Any new fixture, fabricated scenario, code, Contract, or schema change.

## Traceability

Populated in `traceability.yml`.
