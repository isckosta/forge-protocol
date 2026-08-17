# Specification Drift — CHG-0008

## Strict Review Iteration 2 drift
R004 remained partial and R005 established that the Protocol 2 model recorded `revision.commit` but Core compared only `revision.id`. The implementation also lacked an explicit review-subject freeze, so evidence commits after the recorded GREEN commit made the reviewed HEAD ambiguous.

## Normative correction before Resolution 2 implementation
Protocol 2 now distinguishes logical revision identity from concrete immutable revision identity. Provenance may use generic `revision.immutable_ref`; Git `revision.commit` is retained as compatible shorthand. Passed Review requires subject and Reviewer provenance to bind to both the same logical revision and the same normalized immutable revision.

A review subject is frozen only after all reviewable Resolution material is complete. Provenance/review-control metadata may follow the freeze because self-referential commit recording is impossible. Any post-freeze mutation outside the Change-local `manifest.yml`, `provenance.yml`, and `review.md` invalidates the binding and requires new subject provenance.

This correction completes the original Protocol 2 promise of revision-bound provenance; it does not strengthen Protocol 1 and does not claim cryptographic proof for `recorded` evidence.

## Strict Review Iteration 3 drift
R006 established that the Resolution 2 freeze rule was implemented only as a committed-delta check (`git diff <frozen>..HEAD`). That leaves the effective workspace able to diverge from the frozen subject through staged, unstaged, deleted, renamed, or untracked reviewable paths without renewing subject provenance.

## Normative correction before Resolution 3 implementation
For a Git-backed Protocol 2 Change, the review-subject freeze covers the **effective reviewable workspace**, not only committed history. Core must evaluate one reviewable workspace delta relative to the frozen immutable commit, combining committed post-freeze changes, staged changes, unstaged changes, tracked deletions/renames, and Git-visible untracked files. Git-ignored files are not reviewable workspace mutations for this invariant.

The post-freeze exception remains exact and Change-local: only `.forge/changes/<this-change>/manifest.yml`, `provenance.yml`, and `review.md` may differ without invalidating the frozen subject. The exception is matched by repository-root-relative canonical path, never basename, substring, suffix, or directory resemblance. Metadata belonging to another Change remains reviewable with respect to this Change's frozen subject.

Any reviewable workspace delta invalidates the concrete subject binding whenever the Change is relying on frozen subject provenance, including an authoritative `review.status: passed` or Completion state. Pending/failed review states may carry the same diagnostic because their bound subject provenance is already asserting the frozen revision; they do not become review-passed merely because the workspace is clean.

This correction completes the Protocol 2 freeze semantics already promised by `post_freeze_subject_mutation_invalidates_binding`; it does not alter Protocol 1 semantics.
