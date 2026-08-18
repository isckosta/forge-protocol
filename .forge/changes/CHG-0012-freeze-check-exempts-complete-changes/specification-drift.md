---
forge:
  artifact: specification_drift
  schema: 1
change: CHG-0012
status: complete
---
# Specification Drift — CHG-0012

Independent Strict Review Iteration 1 (`review.md`) found a genuine
correctness defect in the first implementation, not merely a documentation
gap: unconditionally exempting `state.current == "complete"` from the
freeze-drift check disabled the check's *true positive* (the Change's own
reviewed files being silently tampered with after Review passed) together
with its *false positive* (unrelated repository activity from other
Changes). `intent.md`'s original Goal section asserted the tradeoff was
safe because "only unrelated activity" would be exempted; that assertion
was false as implemented — the mechanism could not and did not distinguish
the two cases.

- **CHG-0012-R001 (BLOCKER).** Corrected by comparing the frozen subject
  against the first commit where the Change's manifest recorded
  `state.current == "complete"` (`_first_commit_where_state_complete`) via
  `_resolution_delta`, instead of exempting the check outright. This is a
  genuine Requirement correction: the original Goal text is rewritten in
  `intent.md`, not merely the code.

No requirement was weakened to close this Resolution faster. The corrected
version is strictly more protective than the first attempt (it still
detects the exact tampering scenario R001 demonstrated) while remaining
strictly more precise than the pre-CHG-0012 baseline (it no longer fires for
activity unrelated to the Change's own subject, resolving the original CI
breakage).

- **CHG-0012-R002 (BLOCKER, found by independent Resolution Verification
  Iteration 2).** `_first_commit_where_state_complete` trusted the *first*
  commit where `state.current` recorded `complete`, with no check that the
  field never reverted afterward: seal complete → revert to
  `strict_review` → tamper the reviewed file → re-seal complete → zero
  findings, because the drift comparison always targeted the first seal
  commit. This is a resolution regression directly caused by R001's own fix
  introducing `state.current` history as a new trust anchor — before R001,
  no code path trusted that field's history at all. The engineer was
  offered three options (accept as documented residual risk, fix by
  detecting reversion, or revert CHG-0012 entirely) and chose to fix it:
  `_first_commit_where_state_complete` now walks the *entire* history after
  the first seal and returns `None` (falling back to comparing against
  current HEAD/workspace, exactly as for a non-complete Change — the
  original, more conservative behavior) if `state.current` is ever observed
  as anything other than `complete` afterward, or if any post-seal snapshot
  cannot be parsed at all. This is a genuine Requirement correction:
  trusting the *first* seal was itself the defect, not an implementation
  slip; the corrected invariant ("trust a seal only if it was never
  reverted") is what `intent.md`/`inspection.md` should have stated
  originally.
