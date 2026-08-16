# Knowledge Capture — CHG-0008

Protocol compatibility is a semantic boundary. Protocol 1 remains unchanged; Protocol 2 adds independent Execution/Context and concrete revision-bound Strict Review.

A logical revision ID is not a concrete review subject. Protocol 2 normalizes an immutable revision reference and compares it across subject and Reviewer provenance. In Git, commit SHA is the concrete reference.

A provenance record cannot truthfully contain the SHA of the same commit that contains the record. Therefore the reviewable Resolution is frozen first; provenance is review-control metadata committed afterwards and points to the frozen subject.

Strict Review Iteration 3 exposed that a commit SHA does not describe the **effective workspace**. A checkout may contain staged, unstaged, deleted, renamed, or untracked reviewable material while `HEAD` still equals the frozen subject. The durable R006 abstraction is `reviewable workspace delta since frozen subject`: committed delta + index delta + working-tree delta + Git-visible untracked paths, with an exact Change-local metadata exception.

Strict Review Iteration 4 exposed a deeper trust boundary: an allowlisted metadata file cannot also be an unconstrained authority for the baseline from which its own changes are ignored. If current `provenance.yml` can rewrite frozen A to post-freeze B, then a correct filesystem delta from B is still semantically wrong.

The durable R007 rule is therefore **append-only subject authority over Git history**. The first committed representation of a referenced subject provenance record anchors the whole record. Later metadata may append Review/Resolution records or update legitimate review state, but may not rewrite that anchor. Core determines the historical authority before trusting the current immutable reference.

Strict Review Iteration 5 exposed the remaining status-coupling flaw. Historical Review Iteration authority is not a property of a successful or pending verdict; it is a property of the committed identity of the review event. A failed Review is permanent audit evidence that a specific Iteration ID reviewed a specific logical revision through a specific `subject_provenance` record.

The durable R008 rule is therefore **status-independent Review Iteration subject authority**. Once a valid committed representation establishes `iteration.id + revision + subject_provenance`, those identity fields cannot be redirected while retaining or changing the verdict. `pending -> failed` or other lifecycle changes may remain legal when subject identity is unchanged; changing evidence gaps or aggregate counters does not redefine the subject. Previously established bound Iteration IDs must also remain present, so replacing an old ID with a new one cannot bypass the historical lookup. New Iterations with genuinely new IDs remain append-only additions.

Malformed historical YAML is not allowed to manufacture an authority, but neither should an invalid snapshot that predates a later valid binding make that later binding unknowable. The validator may continue looking for the first valid committed representation for the requested Iteration. If complete history is unavailable, Git fails, identity is duplicated/ambiguous, or no safe authority can be determined, validation still fails closed.

This is repository-native rather than provider-native. Complete local Git history is part of the evidence required to resolve committed anchors; shallow history fails closed. The mechanism does not require GitHub or a Forge backend, and it does not claim cryptographic protection against repository-history rewriting.

The metadata exception remains exact. Only the frozen Change's repository-root-relative `manifest.yml`, `provenance.yml`, and `review.md` regular files may differ. Basename matching, a lookalike file, another Change, rename-to-allowlist, a directory named like metadata, or symlink substitution is not review-control metadata.

Review metadata is executable repository state. YAML/schema validity, provenance uniqueness and historical consistency must be validated like implementation artifacts even though the metadata paths have special post-freeze treatment.

`recorded` remains self-recorded repository evidence; `verified` is stronger observer-backed evidence. Core verifies consistency, locality, historical authority, effective workspace freeze, and revision binding, not cryptographic authorship. A Resolver may establish and verify a Resolution subject but cannot certify the independent Strict Review that follows it.
