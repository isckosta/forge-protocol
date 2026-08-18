---
forge:
  artifact: verification
  schema: 1
change: CHG-0013
status: complete
---
# Verification — CHG-0013

## Test evidence

`tests/unit/test_unresolved_decisions.py` (14 tests, TDD-001 through
TDD-012 — see `tdd-evidence.yml`/`traceability.yml`) plus
`tests/contract/test_protocol_contract.py` (validates the new
`decisions` schema field, `policy-decision.schema.json`, the catalog
entry, and every new/edited `.yml` instance against its declared
schema) plus the full existing suite:

```
pytest -q          -> 389 passed (375 pre-existing + 14 new; zero regressions)
forge validate      -> "Forge project is valid" (unchanged from the clean
                        main baseline recorded in plan.md before any code
                        was written)
forge doctor        -> all 7 checks PASS
```

`test_legacy_manifests_are_unaffected` runs `validate_project` directly
against this repository's own `.forge/changes/` (real historical
manifests, not a synthetic fixture) and asserts no finding mentioning
"Decision"/"decisions" appears for any of `CHG-0001` through `CHG-0012` —
the compatibility claim verified directly, not assumed.

## TDD ordering deviation (disclosed, not concealed)

This Change's own Implementation did not follow strict per-behavior TDD
ordering for `_validate_unresolved_decisions`. The full validator function
and the full test file were authored in the same working session, with the
validator written first — a direct deviation from C-009 ("the relevant
behavioral test MUST exist before the production Implementation intended to
satisfy it"). This was not hidden after the fact: before declaring GREEN,
the `validate_project` wiring call was temporarily removed and the complete
test file run against the now-inert validator. 8 of 14 tests failed for the
expected reason (an assertion that a finding would exist received none); 6
passed trivially (positive/compatibility cases that hold with or without
the check). The wiring was then restored, and the full suite, `forge
validate`, and `forge doctor` were re-run clean. `tdd-evidence.yml` records
this exactly, including which specific test names produced the reconstructed
RED, rather than presenting a fabricated clean RED-first history.

This is disclosed here specifically so independent Strict Review can judge
its materiality on its own terms — this session does not adjudicate its own
TDD-discipline defect (C-026, Reviewer/Resolver separation, applies to this
finding as much as to a functional one).

## Adversarial self-check findings (fixed before requesting independent Review)

One design defect was found and fixed during Specification (before
Architecture, recorded in `specification-review.md`), not during
Implementation: the original FR-013/INV-001 wording blocked Gates on any
non-`resolved` status, which would have made a `superseded` Decision block
forever with no path to `resolved` (its successor Decision is the one
expected to reach `resolved`, not the stale record itself). Caught by
adversarial self-review of the Specification text before any code existed,
corrected there, and additionally covered as a permanent regression test
(`test_superseded_decision_does_not_block`, TDD-004) rather than only
documented in prose.

No other design or implementation defect was found during this Change's own
Implementation. This is recorded plainly rather than implying a search that
did not happen — the TDD-ordering deviation above is this Implementation's
one disclosed defect.

## Correction — the original diagnosis of the post-freeze `C-026` finding was wrong

This section originally claimed the `C-026` "review subject changed after
its immutable revision freeze" finding, observed after freezing commit
`40dbfb9` and recording `review-001`/`implementation-001`, was caused
entirely by four untracked paths pre-dating this session
(`.codex/`, `docs/document-2026-08-13T04-46-37-625Z.md`, `docs/superpowers/`,
`uv.lock`), "verified directly, reversibly" via `git stash`.

**Independent Strict Review Iteration 1 (`review.md`, Finding
CHG-0013-R001, BLOCKER) reproduced that exact `git stash` sequence and
found the claim false**: with those four paths removed from the working
tree, `forge validate` still reported the same `C-026` finding. The actual
root cause, found by the Reviewer tracing `_review_control_metadata_paths`
in `src/forge_cli/validation/__init__.py`: the review-control metadata
exception in Protocol 2 §5 is exactly
`{manifest.yml, provenance.yml, review.md}` — **not `verification.md`**.
The post-freeze metadata commit (`ba5b880`) modified `verification.md`
itself (this file, adding the very paragraph making the false claim) —
a genuine, real mutation of the frozen subject outside the exempted set,
which is exactly what invalidated the freeze. The stash-based diagnosis
was internally consistent as an experiment but drew the wrong conclusion
from a coincidence: removing the four unrelated untracked paths does not
explain the finding; the real cause was this file's own post-freeze edit.

This is corrected here rather than silently amended: the original
(incorrect) diagnosis is preserved above in "Not yet independently
verified" history via Git, and this correction is itself part of the
Resolution `git diff` for `CHG-0013-R001` (see `review.md` for the
Reviewer's full finding and `manifest.yml`/`provenance.yml` for the
corrected freeze at `implementation-002`).

## Resolution of independent Strict Review Iteration 1 findings

Full findings and verdict: `review.md`. Summary of Resolution actions,
each performed with Reviewer/Resolver role separation preserved (this
Resolution was authored by the original Implementation session — a
distinct independent Execution/Context is required again for the
Resolution *Verification* that follows, not for the Resolution itself,
consistent with how CHG-0011 handled its own Resolution 1):

- **CHG-0013-R001 (BLOCKER)** — fixed. Root cause corrected above.
  `implementation-001` is superseded by `implementation-002`, a fresh
  freeze commit containing the corrected `verification.md` plus the
  R002/R003 code fixes below, so `verification.md`'s content is now
  genuinely part of the frozen subject rather than a post-freeze mutation
  of it. `review-001` is updated to reference `implementation-002`.
- **CHG-0013-R002 (MAJOR)** — fixed with proper TDD this time: two new
  tests (`test_product_class_below_human_authority_floor_is_a_finding`,
  `test_contract_class_below_human_authority_floor_is_a_finding`) were
  written first, run, and confirmed to fail for the expected reason (no
  finding produced) before `_DEC_AUTHORITY_FLOOR`/the floor check was
  added to `_validate_unresolved_decisions`. A third test
  (`test_architectural_and_technical_classes_are_not_floor_restricted`)
  proves the floor does not over-apply to the two classes that were never
  meant to carry it.
- **CHG-0013-R003 (MINOR)** — fixed with proper TDD: one new test
  (`test_invalidates_target_missing_from_artifacts_is_a_finding`) written
  and confirmed failing first, then the C-057 check corrected to treat a
  key entirely absent from `artifacts` as a finding, not a silent pass.
- **CHG-0013-R004 (MAJOR, TDD-ordering deviation)** — not unilaterally
  self-graded. Per the Reviewer's own instruction ("this needs an explicit
  accept/reject engineering decision, not silent pass-through"), this is
  presented to the human user as a genuine Decision, using this Change's
  own structured format, in the session's final report. Completion does
  not proceed until that Decision is recorded.
- **CHG-0013-R005 (OBSERVATION)** — accepted as documented follow-up, not
  fixed now (matches the Reviewer's own assessment: consistent with
  `architecture.md`'s declared validator scope, not a broken promise).
  Recorded in `knowledge-capture.md`.
- **CHG-0013-R006 (OBSERVATION)** — accepted as documented follow-up, not
  fixed now (same precedent as the pre-existing `C-026` umbrella-code
  convention; low impact, `code` is display-only). Recorded in
  `knowledge-capture.md`.

Post-Resolution verification: `pytest -q` → 393 passed (375 original + 18
in `test_unresolved_decisions.py`, up from 14); `forge validate` and
`forge doctor` re-run after the corrected freeze (see below).

## Re-verification of the untracked-files condition against the new freeze

After freezing `resolution-001` (commit `abf3bbb`) and recording
`review-002` as `pending`, `forge validate` again reports the `C-026`
finding. Re-verified independently against *this* freeze, the same way
Strict Review Iteration 1 verified the original claim (not assumed to
still hold from before): `git stash push -u -- .codex
docs/document-2026-08-13T04-46-37-625Z.md docs/superpowers uv.lock`
followed by `forge validate` returns "Forge project is valid"; `git stash
pop` restores the four paths, confirmed via `git status --short`
afterward. This time the only uncommitted change besides those four paths
is `manifest.yml`/`provenance.yml` themselves (both exempt), so the
four untracked paths are confirmed, again, to be the sole cause — this
time against the corrected subject, not the broken one R001 was raised
against.

## Not yet independently verified

A Resolution Verification (or fresh Initial Review) of `resolution-001`
in a separate Execution and Execution Context from both this Implementation
session and Review Iteration 1 is required before Completion (`tasks.md`
T-015/T-016).
