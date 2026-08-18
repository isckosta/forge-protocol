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

## Pre-existing environmental condition (disclosed, not fixed here)

After freezing this Change's Implementation subject (commit `40dbfb9`) and
recording `review-001` as `pending` in `manifest.yml`, `forge validate`
reports one `C-026` finding: "review subject changed after its immutable
revision freeze." This is caused entirely by four untracked paths that
pre-date this session and are not part of CHG-0013's diff — `.codex/`,
`docs/document-2026-08-13T04-46-37-625Z.md`, `docs/superpowers/`, and
`uv.lock` — present in this repository's working tree before any work on
this Change began. Verified directly, reversibly, and without modifying
them: `git stash push -u -- .codex docs/document-2026-08-13T04-46-37-625Z.md
docs/superpowers uv.lock` followed by `forge validate` returns "Forge
project is valid" with those four paths set aside; `git stash pop`
restores them unchanged. This is the same class of pre-existing,
out-of-declared-scope condition CHG-0011's own `verification.md` recorded
for `CHG-0008`'s manifest — not introduced by this Change, not fixed by
this Change (deciding whether those four paths should be tracked or
`.gitignore`d is a repository-hygiene judgment call unrelated to
Unresolved Decision Management and not this session's to make
unilaterally). Flagged here for the user/maintainer rather than silently
routed around.

## Not yet independently verified

Reviewer/Resolver independence for CHG-0013's own subject requires a Strict
Review Iteration in a separate Execution and Execution Context from this
Implementation session (`tasks.md` T-015), executed after this
Implementation freezes its subject (`provenance.yml`).
