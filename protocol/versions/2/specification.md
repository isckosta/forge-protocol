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

In a Git repository, an explicit `git_commit` subject MUST exist locally. Once the subject is frozen, commits that change implementation, tests, specification, verification evidence, documentation, or other subject material invalidate that binding and require new subject provenance. Only review-control metadata needed to record the freeze and the independent Review may follow without changing the subject: that Change's `manifest.yml`, `provenance.yml`, and `review.md`.

This resolves the self-reference problem: the frozen subject commit contains the complete reviewable Resolution state; a later metadata commit records provenance pointing to that already-existing immutable subject. The Reviewer is authorized to judge the frozen subject, not an ambiguous later HEAD.

## 6. Review Iterations and re-review
A passed iteration references subject and Reviewer provenance. Both records MUST bind to the same `revision.id` and the same normalized immutable reference. Reviewer Execution and Context MUST each differ from the subject Execution and Context.

Canonical lifecycle:

Implementation → frozen revision A → Review 1 → blocking Findings → Resolution → frozen revision B → subject provenance for B → Review 2 of B.

A re-review MUST use the provenance that produced the resolved concrete revision, never stale provenance from an earlier revision.

## 7. Change/schema boundary
Protocol 2 active Changes use `forge/change@2`; completed historical Protocol 1 Changes may remain `forge/change@1`. Execution provenance uses `forge/execution-provenance@1`. Schema and Protocol versions remain independent axes.

## 8. Completion
Completion MUST NOT occur when a passed Strict Review lacks sufficient subject/Reviewer provenance, when logical or concrete revision binding diverges, when the frozen subject changed without renewed provenance, when assurance is only `claimed`, when Execution or Context is shared, or when schema downgrade is used to bypass Protocol 2.

## 9. Compatibility and evolution
Protocol 1 remains frozen. Protocol 2 is the first integer Protocol version requiring independent Execution/Context and concrete revision-bound provenance. CHG-0008 defines Protocol 2 before release; corrections made inside this still-unmerged Change complete that original semantic promise rather than retroactively changing a released Protocol 2 instance.
