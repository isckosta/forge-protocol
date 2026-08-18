---
forge:
  artifact: verification
  schema: 1
change: CHG-0011
status: complete
---
# Verification — CHG-0011

## Test evidence
`tests/unit/test_resolution_verification.py` (14 tests, TDD-012, TDD-013,
TDD-014, TDD-016, and a subset of TDD-020) plus the full existing suite:

```
pytest -q          -> 242 passed (228 pre-existing + 14 new; zero regressions)
forge validate      -> exit 2, exactly one finding, unchanged from a clean
                        `main` checkout with none of this Change's edits
                        applied (independently confirmed by checking out
                        main into a throwaway worktree and running the same
                        command before writing any code): a pre-existing,
                        out-of-scope C-026 freeze finding on CHG-0008's
                        already-`complete` manifest, caused by that
                        manifest's individual passed Iteration still
                        comparing against current HEAD. Not introduced by
                        this Change; not fixed by this Change (out of
                        declared scope — see Remaining risks).
forge doctor         -> exit 0, all checks PASS
```

`test_legacy_manifests_are_unaffected` runs `validate_project` directly
against this repository's own `.forge/changes/` (not a synthetic fixture) and
asserts no finding produced by this Change's new logic appears for
`CHG-0008` or `CHG-0010` — AC-001/AC-012 verified directly, not assumed.

## Adversarial self-check findings (fixed before requesting independent Review)
Two real design/implementation defects were found and fixed during this
Change's own Implementation, per the mandated self-check (this session's
operating instructions §20):

1. **Resettable convergence counter (INV-003 violation).** The first
   implementation derived `consecutive_unconverged_verifications` only as a
   *trailing* run. Appending a fresh `initial_review` Iteration after
   Non-Convergence silently reset the trailing run to 0, so the
   "decision required" check never fired for an episode that was never
   actually decided — exactly the resettable-counter bypass this Change
   exists to prevent. Fixed by scanning the full historical `iterations`
   array for every point the limit was reached, independent of the current
   trailing state. Caught by `test_convergence_limit_allows_new_initial_
   review_after_decision` initially passing for the wrong reason (no
   finding was raised at all, because the check never activated) — the fix
   was verified by confirming the sibling test
   `test_convergence_limit_blocks_further_resolution_verification_without_
   decision` still fails correctly.
2. **Full Review Escalation not enforced on first occurrence.** The
   original implementation only rejected a further `resolution_verification`
   Iteration through the Convergence Limit path (requiring 2 qualifying
   entries), so a *single* `full_review_required: true` Iteration did not,
   by itself, block an immediately following illegitimate
   `resolution_verification` — contradicting FR-010/§11. Caught directly by
   `test_out_of_scope_mutation_with_full_review_required_validates`'s second
   assertion failing (`assert not result2.passed` received `True`). Fixed
   with an independent, unconditional check for the `full_review_required`
   case, separate from the Convergence Limit path.

Both were caught by tests written *before* the fix existed and observed to
fail for the correct causal reason (RED), then fixed (GREEN) — TDD applied
to the validator's own adversarial edge cases, not only its golden path.

## Not yet independently verified
Reviewer/Resolver independence (Execution/Context separation, freeze,
provenance authority) for CHG-0011's own subject requires a Strict Review
Iteration in a separate Execution and Execution Context from this
Implementation session. That Iteration is `plan.md` T-014, executed after
this Implementation freezes its subject — see `review.md`.
