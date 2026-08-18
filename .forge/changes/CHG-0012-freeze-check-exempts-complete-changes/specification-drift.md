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
