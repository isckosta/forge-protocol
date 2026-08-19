---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0015
status: approved
---

# Test Strategy — CHG-0015

Two test levels, matching the two kinds of claim this mechanism makes:

- **Shape/logic tests** (`tests/unit/test_validation.py` conventions,
  `tmp_path` fixture manifests + provenance files, no real Git history) —
  for record-shape validation, the Delegation Ceiling's static comparison
  logic, and Gate-blocking interactions. Mirrors `CHG-0013`'s approach for
  Unresolved Decision Management.
- **Fixture-repo tests** (`tmp_path` + real `git init`/`git commit`/real
  working-tree mutations via subprocess, `CHG-0011`'s Resolution Delta
  convention) — required for `_delegated_execution_effect` and the
  `baseline`/`dirty` capture, since this half of the mechanism makes a
  factual claim about real Git-observable state, not just YAML shape. A
  pure-mock test of Git behavior would not satisfy AC-011 ("independent
  verification... not merely assert that instructional prompt text
  forbids mutation").

Per this Change's own C-008/C-009 (TDD-first, RED before production), every
`TDD-NNN` below starts RED: the referenced function/field does not exist
yet, so the first test run fails for `AttributeError`/`KeyError`/schema-
rejection reasons — the expected "absent behavior" failure — not an
environment failure (C-011).

## TDD-001 — legacy/compatibility baseline (RED first)

Load every real `provenance.yml` under `.forge/changes/CHG-0001`..
`CHG-0015` (none declares `role: delegated_task`) through
`_validate_delegated_authority` directly. Expect zero findings from this
function specifically, for all of them — the compatibility invariant
(FR-015/AC-010) as an executable test, not only an architectural claim.

## TDD-002 — pure read-only delegate that only reads (golden path)

Fixture repo, one commit. `baseline` captured (clean `dirty` map). Delegate
performs no filesystem mutation at all. `close` captured (identical `dirty`
map). `scope: []`. Expect `_delegated_execution_effect` returns an empty
set and `_validate_delegated_authority` reports zero findings.

## TDD-003 — the incident class (AC-012, THE required test)

Fixture repo reproducing the actual `CHG-0014` incident's shape
mechanically, independent of any AI provider:

1. Commit a baseline state including `intent.md` and `discovery.md`.
2. Simulate the primary Execution already mid-Discovery: leave
   `discovery.md` genuinely dirty (uncommitted edit) *before* capturing
   `baseline` — this is the realistic pre-condition the incident actually
   had.
3. Capture `baseline` (`head` + `dirty` map, which now legitimately
   includes `discovery.md`).
4. Simulate the delegate (`scope: []`, read-only): overwrite `intent.md`
   directly on disk (no commit) — the exact incident action.
5. Capture `close`.

Expect: `_delegated_execution_effect` returns exactly `{intent.md}` — the
primary Execution's own pre-existing `discovery.md` edit MUST NOT appear
(proving the `dirty`-baseline attribution design actually works, not just
reads correctly on paper). `_validate_delegated_authority` reports exactly
one finding: **C-061 (Out-of-Scope Mutation)**, not C-062 — `intent.md` is
an ordinary Artifact, not an Authority-Defining one, so this is correctly
classified as scope violation, not self-authorization (Specification's own
note on this distinction, re-verified here as a test, not only asserted in
prose).

## TDD-004 — scoped writer within declared paths (golden path)

`scope: ["tests/fixtures/example.py"]`; delegate writes only that path.
Expect zero findings.

## TDD-005 — scoped writer partially outside declared paths

`scope: ["tests/fixtures/example.py"]`; delegate writes that path **and**
`src/forge_cli/unrelated.py`. Expect exactly one finding, naming only the
unrelated path — proves partial-scope correctness (not an all-or-nothing
check that would either over- or under-report).

## TDD-006 — self-authorization (C-062) — regression test for the
Architecture-stage fix

`scope: []`; delegate directly rewrites its **own already-recorded**
`provenance.yml` entry, editing that record's `scope` field from `[]` to a
broader grant it was never actually given — the exact escalation shape
originating instruction §16/§24 warns against (an Execution modifying the
document that defines its own Authority). Expect exactly one finding,
classified **C-062**, not the generic C-061. This is
the direct regression test for the defect `architecture.md` records
finding and fixing (the review-control-metadata exclusion that would have
made this invisible) — written explicitly so a future regression of that
exclusion fails this test first, not silently.

## TDD-007 — Delegation Ceiling, first hop, conservative default exceeded

Primary Execution's own provenance record declares no `scope` (the common
case under DEC-001). Delegate is granted `scope: ["docs/unrelated.md"]`, a
path outside this Change's own governed paths
(`.forge/changes/CHG-0015-*/**` plus its declared `src`/`tests` paths).
Expect one finding: the grant itself exceeds the conservative default.
This check depends only on the `scope` declared in the delegate's
provenance record, not on its Observed Effect — so it is checkable as
soon as the delegate's record exists, independent of TDD-003/005's
Observed-Effect checks — but it is still `forge validate`-mediated
Detection (C-064), not Prevention: nothing here stops the delegate from
running with the excessive grant, only from that run being accepted as
valid afterward. Test asserts the finding fires; it does not assert
anything about *when* in real time a human or harness would see it.

## TDD-008 — Delegation Ceiling, first hop, within conservative default

Same as TDD-007 but `scope` is a path inside the Change's own governed
area. Expect zero findings from this check.

## TDD-009 — nested delegation narrows correctly

`delegated_task` A: `scope: ["src/a/f1.py", "src/a/f2.py"]`. A delegates to
nested `delegated_task` B (`execution.delegated_by` = A's id):
`scope: ["src/a/f1.py"]` (subset). Expect zero Delegation Ceiling findings
for the A→B edge.

## TDD-010 — nested delegation attempts to widen

Same A as TDD-009. B's `scope: ["src/a/f1.py", "src/b/f2.py"]` — not a
subset (`src/b/f2.py` outside A's grant). Expect exactly one C-063 finding
naming the excess path, checked transitively (FR-008), not only at the
first hop.

## TDD-011 — missing delegator reference (provenance gap)

`delegated_task` record's `execution.delegated_by` names an `execution.id`
absent from the same ledger. Expect one finding: Delegation Ceiling cannot
be established (fail-closed, distinct message from an actual ceiling
violation).

## TDD-012 — fail-closed on unavailable baseline history (C-065/INV-005)

`baseline.head` names a commit not present in the fixture repo's local
history (simulated shallow clone: create the commit in a throwaway repo,
copy only a later commit into the fixture, omit the object). Expect
`_delegated_execution_effect` returns `None`, and
`_validate_delegated_authority` reports a distinct "cannot verify" finding
— **not** zero findings (which would be the fail-*open* bug this
invariant exists to prevent).

## TDD-013 — `delegated_task` record missing `scope` entirely (shape, C-060)

`role: delegated_task` with no `scope` key at all (distinct from
`scope: []`). Expect one finding — `scope` presence (possibly empty) is
mandatory for this role; absence is not equivalent to "no restriction."

## TDD-014 — schema-level `scope: []` acceptance (`forge/execution-
provenance@2`)

Direct `jsonschema.Draft202012Validator` validation (matching this
repository's own `tests/contract/test_protocol_contract.py` convention) of
a `role: delegated_task` record with `scope: []` against
`execution-provenance-v2.schema.json`. Expect it validates — the concrete
regression test for the `minItems: 0` relaxation Architecture records as a
deliberate, disclosed schema change from `@1`. A companion assertion
confirms an `@1` record with `scope: []` still **fails** `@1`'s own
(unrelaxed) schema — proving the relaxation is `@2`-scoped, not a silent
loosening of `@1`.

## TDD-015 — absence of `provenance.yml` entirely (compatibility, distinct
from TDD-001)

A synthetic minimal manifest with no `provenance.yml` at all (not just no
`delegated_task` entries within one). Expect zero findings from
`_validate_delegated_authority` — the absence-of-file compatibility case,
separate from TDD-001's "real historical files with no matching role"
case, since the two code paths (missing file vs. missing matching record)
are not necessarily the same branch.

## TDD-016 — baseline/close capture failure is fail-closed, not silent

Simulate the underlying `git` invocation itself failing during baseline or
close capture (non-zero exit, e.g., a corrupted `.git` or a permission
error on the fixture — same technique `_git_root`'s existing `None`-return
convention already uses elsewhere in this file). Expect the capture
function itself signals failure distinctly from "no changes observed," and
`_validate_delegated_authority` treats it as C-065 fail-closed, not as a
clean pass. This is the bounded, testable slice of the TOCTOU/concurrency
limitation Architecture explicitly disclaims solving in general — it tests
that the *fallback* behavior is correct, not that concurrency itself is
solved.

## Traceability (informal — `traceability.yml` itself is a Plan/Tasks-stage
deliverable, not duplicated here)

| Requirement | Covered by |
|---|---|
| FR-001/FR-003 (Scope representable, incl. empty) | TDD-002, TDD-013, TDD-014 |
| FR-004 (stage-agnostic Execution Boundary) | TDD-003 (anchored pre-freeze, Discovery-shaped) |
| FR-005/C-061/INV-004 (Out-of-Scope Mutation) | TDD-003, TDD-005 |
| FR-006/C-062/INV-002 (self-authorization) | TDD-006 |
| FR-007/FR-008/C-063/INV-003 (Delegation Ceiling, incl. nested) | TDD-007, TDD-008, TDD-009, TDD-010 |
| FR-009 (attribution/provenance gap) | TDD-011 |
| FR-011/C-064 (Detection floor) | TDD-002 through TDD-012 collectively |
| FR-013/C-065/INV-005 (fail-closed) | TDD-011, TDD-012, TDD-016 |
| AC-010/FR-015 (historical compatibility) | TDD-001, TDD-015 |
| AC-012 (original incident class) | TDD-003 |

C-066/FR-014 (harness honesty) has no dedicated behavioral test: Discovery
and Architecture both established no Adapter/CLI text in this repository
currently claims Prevention anywhere, so the property is presently
vacuous, not untested-but-real. A lightweight grep-based regression guard
(no projected/generated string contains an unqualified "enforced" claim
for delegated-Execution authority) is proportional; a richer behavioral
test is deferred until a real Prevention mechanism exists to conflate
against (Architecture's own "deliberately not built now").

## Verification

`pytest -q`, `forge validate` (must remain "Forge project is valid" — no
regression against the state confirmed at the end of Architecture),
`forge doctor`, plus direct `jsonschema.Draft202012Validator` validation of
this Change's own `manifest.yml` and any fixture-repo provenance files
against their respective schemas (matching `CHG-0014` Strict Review's own
verification convention of not trusting `forge validate` alone for schema
conformance).
