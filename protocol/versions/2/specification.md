# Forge Core Protocol Specification — Protocol 2

Protocol version: `2`  
Status: Stable

## 1. Compatibility basis
Protocol 2 inherits unchanged Protocol 1 Flow, TDD, Verification, Documentation, locality, provider-independence, Adapter, and repository-authority semantics. Protocol 1 remains authoritative for Protocol 1 instances and is not retroactively strengthened.

## 2. Strict Review
A Strict Review that can satisfy `review_passed` MUST run in an Execution and Execution Context distinct from the Implementation or Resolution that produced the review subject. Role switching inside one context is self-review. This applies to FAST, STANDARD, and FULL.

## 3. Execution provenance
Protocol 2 uses repository-native execution provenance. Every record identifies Role, Execution ID, Context ID, capture time, logical revision identity, a concrete immutable revision reference, and evidence source/assurance.

`revision.id` is the logical revision identity. It is not sufficient concrete binding by itself. `revision.immutable_ref` is the provider/VCS-neutral concrete identity. For Git, `revision.commit` remains a compatible shorthand for `immutable_ref: {type: git_commit, value: <sha>}`; when both are present they MUST agree.

Supported immutable-reference kinds may include Git commits, content digests, or another immutable VCS revision. Core compares the normalized immutable reference, not merely a mutable alias.

## 4. Assurance
`claimed` is declaration only. `recorded` is durable repository-native self-recorded evidence and is the minimum for `review_passed`. `verified` adds observer-backed evidence. Recorded provenance is not cryptographic or external proof. Core mechanically verifies record existence, Role, assurance, logical/concrete revision consistency, and Execution/Context separation.

## 5. Review subject freeze
A Review Iteration evaluates one frozen subject. The subject provenance MUST identify both the logical revision and the concrete immutable revision produced by Implementation or Resolution. Reviewer provenance MUST identify the exact same logical and concrete revision.

In a Git repository, an explicit `git_commit` subject MUST exist locally. Once the subject is frozen, the **effective reviewable workspace** MUST remain equivalent to that frozen subject except for the narrow review-control metadata exception below. Core MUST account for reviewable deltas introduced by committed post-freeze changes, the index/staging area, the unstaged working tree, tracked deletion or rename, and Git-visible untracked files. Files excluded by Git ignore rules are not reviewable workspace mutations for this invariant.

The only post-freeze paths that MAY differ without renewing subject provenance are the frozen Change's exact repository-root-relative `manifest.yml`, `provenance.yml`, and `review.md` paths. The exception MUST NOT be inferred from basename, substring, suffix, directory resemblance, or membership in the Change directory generally. A reviewable path renamed to an allowed path remains a subject mutation, and review-control paths that are replaced by non-regular or symlink entries do not qualify for the exception.

The metadata exception does **not** make an existing frozen-subject binding mutable. For Git-backed provenance, the first committed representation of a referenced subject provenance record is the repository-native immutable authority for that record. Its Role, Execution, Execution Context, logical revision, concrete immutable revision, assurance/source fields, and record identity MUST NOT later be rewritten, replaced, removed and recreated with different semantics, or shadowed by a duplicate ID. Likewise, once a Review Iteration's `revision` and `subject_provenance` binding has a committed representation, later review-control metadata MUST NOT redirect that Iteration to another subject record or logical revision.

Core MUST establish these authorities from committed repository history **before** using the current provenance value as the baseline for effective-workspace comparison. Appending a new provenance record, adding independent Reviewer provenance, or updating other legitimate review-control metadata remains allowed when previously anchored subject records and Iteration subject bindings remain unchanged. This removes circular authority: mutable `provenance.yml` may carry new metadata, but it cannot redefine the historical baseline whose mutations it is allowed to exclude.

When Git history is required to establish that authority, Core MUST fail closed if the repository root, committed history, or historical record cannot be determined reliably. A shallow/incomplete Git history is insufficient for an existing anchored subject; callers that validate such a subject MUST provide complete local history. This requirement remains local and provider-independent and does not require GitHub, a Forge backend, or another hosted service.

Any other mutation to implementation, tests, specification, verification evidence, documentation, Change artifacts, normative Protocol resources, or other subject material invalidates that binding and requires new subject provenance whether or not the mutation has been committed.

The freeze therefore avoids self-reference: the frozen subject commit contains the complete reviewable Resolution state; a subsequent metadata commit records subject provenance pointing back to that commit and becomes the first committed authority for the record. Later metadata records may record provenance and independent Review state while the reviewable workspace itself remains frozen. The Reviewer is authorized to judge that anchored frozen subject, not an ambiguous later HEAD or a mutable current provenance claim.

## 6. Review Iterations and re-review
A passed iteration references subject and Reviewer provenance. Both records MUST bind to the same `revision.id` and the same normalized immutable reference. Reviewer Execution and Context MUST each differ from the subject Execution and Context.

Canonical lifecycle:

Implementation → frozen revision A → subject provenance for A → Review 1 → blocking Findings → Resolution → frozen revision B → subject provenance for B → Review 2 of B.

A re-review MUST use the provenance that produced the resolved concrete revision, never stale provenance from an earlier revision. Historical Iteration subject bindings are append-only in meaning once committed.

## 7. Change/schema boundary
Protocol 2 active Changes use `forge/change@2`; completed historical Protocol 1 Changes may remain `forge/change@1`. Execution provenance uses `forge/execution-provenance@1`. Schema and Protocol versions remain independent axes.

## 8. Completion
Completion MUST NOT occur when a passed Strict Review lacks sufficient subject/Reviewer provenance, when logical or concrete revision binding diverges, when historical subject provenance or an Iteration subject binding has been rewritten, when required Git authority cannot be determined reliably, when the frozen reviewable workspace has changed without renewed provenance, when assurance is only `claimed`, when Execution or Context is shared, or when schema downgrade is used to bypass Protocol 2.

## 9. Compatibility and evolution
Protocol 1 remains frozen. Protocol 2 is the first integer Protocol version requiring independent Execution/Context and concrete revision-bound provenance. CHG-0008 defines Protocol 2 before release; corrections made inside this still-unmerged Change complete that original semantic promise rather than retroactively changing a released Protocol 2 instance.
