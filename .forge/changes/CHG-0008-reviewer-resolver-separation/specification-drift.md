# Specification Drift — CHG-0008

## Strict Review Iteration 2 drift
R004 remained partial and R005 established that the Protocol 2 model recorded `revision.commit` but Core compared only `revision.id`. The implementation also lacked an explicit review-subject freeze, so evidence commits after the recorded GREEN commit made the reviewed HEAD ambiguous.

## Normative correction before Resolution 2 implementation
Protocol 2 now distinguishes logical revision identity from concrete immutable revision identity. Provenance may use generic `revision.immutable_ref`; Git `revision.commit` is retained as compatible shorthand. Passed Review requires subject and Reviewer provenance to bind to both the same logical revision and the same normalized immutable revision.

A review subject is frozen only after all reviewable Resolution material is complete. Provenance/review-control metadata may follow the freeze because self-referential commit recording is impossible. Any post-freeze mutation outside the Change-local `manifest.yml`, `provenance.yml`, and `review.md` invalidates the binding and requires new subject provenance.

This correction completes the original Protocol 2 promise of revision-bound provenance; it does not strengthen Protocol 1 and does not claim cryptographic proof for `recorded` evidence.
