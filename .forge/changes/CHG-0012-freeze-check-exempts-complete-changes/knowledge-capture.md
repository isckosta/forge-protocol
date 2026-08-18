---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0012
status: complete
---
# Knowledge Capture — CHG-0012

- **A hotfix to a mechanical review-gating invariant is itself high-stakes
  engineering, not a formality.** This Change looked like a one-line fix
  and took four independent Strict Review Iterations, three genuine
  BLOCKERs, a formal Non-Convergence event, and an explicit engineering
  decision to resolve responsibly. Treating it with FAST-flow ceremony
  (Intent/Inspection/TDD/Verification/Review, no Architecture) was the
  right classification — it never needed Architecture-level planning — but
  "small diff" and "small stakes" are not the same thing when the diff
  touches a Contract-level (C-026) invariant every other Change's
  Completion depends on.
- **Inferring trust from a mutable, hand-editable field's history is a
  recurring failure shape, not a one-off mistake.** Three consecutive
  attempts (trust the first occurrence; trust the first occurrence unless
  reverted; walk the full history for reverts) each closed one gap and
  opened another, because the field (`state.current`) itself has no
  programmatic gate anywhere in this codebase. The lesson generalizes
  beyond this Change: before building a mechanism that reasons about
  *when* a self-declared field became trustworthy, ask whether the field
  can be made structurally trustworthy instead (a real gate), or whether
  the mechanism should stop depending on it at all.
- **A structurally stronger fix can still be the wrong fix.** Attempt 4
  (scope to the implementation's own touched paths) was provably more
  secure than the shipped final version — it closed all three discovered
  BLOCKERs. It was not adopted because it traded a security gap for a
  real, immediately-observed operational cost (breaking CHG-0011's own
  validation the moment this Change's own implementation touched a shared
  file). "More secure" and "the right trade-off for this system" are not
  automatically the same conclusion, and discovering that requires actually
  building and testing the alternative against the live repository, not
  just reasoning about it abstractly.
- **CHG-0011's Non-Convergence mechanism worked exactly as designed, on the
  first Change other than itself.** Independent Resolution Verification
  Iteration 3 detected the second consecutive independent finding, recorded
  `review.convergence.state: review_convergence_failed`, and stopped rather
  than attempting a fourth automatic fix — dogfooding CHG-0011's own
  mechanism under real, unplanned pressure (an urgent CI-breaking bug),
  which is a stronger validation than any test fixture could provide.
- **Accepting a residual risk is not the same as ignoring it.** The final
  shipped code is *identical in shape* to the version independent Strict
  Review Iteration 1 originally rejected (CHG-0012-R001). The difference is
  entirely in what the artifacts say about it: the first attempt asserted
  (incorrectly) that only unrelated activity was exempted; the final
  version explicitly documents, in `specification-drift.md`, exactly what
  risk is accepted and why. Per C-040 ("Explicit trade-offs"), that
  documentation is the entire difference between a silently reintroduced
  defect and a legitimate engineering decision.

## Follow-up (not implemented in this Change)

If this residual risk (CHG-0012-R001/R002/R003's shared root cause) is ever
judged unacceptable in the future, Attempt 4 (`_implementation_touched_paths`
— described in full in `specification-drift.md`; implemented, verified
against all three prior BLOCKERs, then reverted before being committed, so
it exists only in this Change's engineering record, not in Git history) is
a proven, working starting point — its remaining problem (operational
friction on shared/hot files for already-complete Changes) would need a
companion mechanism to let a completed Change "re-seal" its subject after a
disclosed, legitimate later edit without requiring a full new Strict
Review — which does not exist today and was explicitly out of scope for
this Change to design under CI-breaking time pressure.
