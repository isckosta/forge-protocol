# Forge Core Protocol Specification — Protocol 2

Protocol version: `2`

Status: Stable

## 1. Compatibility basis

Protocol 2 inherits Protocol 1 sections 1–21, 23–24, 26, 28–37 and all unchanged Flow, TDD, Verification, Documentation, provider-independence, locality, Adapter, and repository-authority semantics. The Protocol 1 specification remains authoritative for Protocol 1 instances at `protocol/specification.md`; Protocol 2 does not retroactively reinterpret them.

Protocol 2 intentionally strengthens Strict Review independence. This is a breaking Core semantic change and therefore uses integer Protocol identifier `2`, independently from artifact schema identifiers such as `forge/change@2`.

## 2. Strict Review

Every Change MUST undergo adversarial Strict Review. Under Protocol 2, a Strict Review that can satisfy `review_passed` MUST be produced by a Review Execution whose concrete Execution and transient Execution Context are distinct from the Implementation or Resolution execution that produced the revision under review.

Changing Role inside the same conversation, thread, session, invocation, or reasoning context is self-review. Self-review MAY be performed as a quality activity but MUST NOT satisfy Strict Review.

The rule applies equally to FAST, STANDARD, and FULL. FAST reduces ceremony, not review quality.

When an active external review surface exists, unresolved blocking threads continue to block `review_passed` exactly as in Protocol 1.

## 3. Execution provenance

Protocol 2 introduces repository-native execution provenance as the durable evidence boundary for Strict Review.

A provenance record MUST identify:

- a stable record identifier;
- the Forge Role performed by the execution (`implementation`, `resolution`, or `review`);
- provider-independent `execution.id` and `execution.context_id` values;
- the time at which the record was written;
- the revision identifier produced or reviewed, with a commit reference when available;
- the source and assurance level of the evidence.

Harnesses and Adapters MAY map native run, thread, conversation, session, workspace, invocation, or equivalent identifiers into the Core execution/context fields. Core semantics MUST NOT depend on any provider-specific term.

## 4. Assurance levels

Protocol 2 distinguishes three assurance levels:

1. `claimed` — an identity declaration with no durable execution record suitable for the Strict Review Gate;
2. `recorded` — repository-native provenance captured for an execution and linked to its revision; this is the minimum Core evidence accepted for `review_passed`;
3. `verified` — provenance additionally observed by a Harness, Adapter, operator, attestation mechanism, or equivalent source.

The Core validator MUST NOT describe pairwise-distinct strings as proof of independence. It verifies that referenced records exist, have sufficient assurance, bind to the revision under review, carry the required roles, and do not share execution/context identifiers. A malicious author could still falsify a self-recorded repository record; Forge therefore does not claim cryptographic or external proof unless a stronger verification source actually supplies it.

Protocol 2 does not require a hosted Forge backend. Verified provenance is optional Core strengthening, not a remote-infrastructure requirement.

## 5. Review Iterations and revision binding

Review state is iteration-oriented rather than represented by one global Resolver identity.

A Review Iteration MUST identify the revision it evaluates. A passed iteration MUST reference:

- subject provenance for the Implementation or Resolution that produced that revision; and
- Reviewer provenance for the Review Execution evaluating that same revision.

Both provenance records MUST bind to that revision. The Reviewer execution ID and context ID MUST each differ from the corresponding subject execution/context identifiers.

This permits the canonical sequence:

Implementation Execution → revision A → Review Iteration 1 → blocking Findings

Resolution Execution → revision B → Review Iteration 2

The re-review of revision B MUST compare the Reviewer to the Resolution provenance that produced B, not to a stale global Resolver field from revision A.

## 6. Resolution and re-review

A Resolver MUST NOT resolve blocking Findings inside the Reviewer's Execution Context. After blocking Findings are resolved, acceptance requires a new Review Iteration whose Reviewer provenance is independent from the Resolution Execution and Context that produced the resolved revision.

The same human, Harness, provider, model, or agent implementation MAY perform another stage if a real independent Execution and Context are used. Role renaming alone never creates independence.

## 7. Change schema boundary

Protocol 1 historical Changes continue to use `forge/change@1` with their original meaning. Protocol 2 active Changes MUST use `forge/change@2` so they cannot downgrade artifact shape to escape the Protocol 2 review Gate. A Protocol 2 project MAY retain completed historical `forge/change@1` instances without rewriting them or fabricating provenance.

`forge/change@2` records Review Iterations and declares `protocol: 2`. Execution provenance is stored in `provenance.yml` using `forge/execution-provenance@1`.

Artifact schema version and Protocol version remain independent axes: the `@2` suffix does not itself create Protocol 2 semantics, and Protocol 1 was not changed merely because a new schema file exists.

## 8. Completion

Protocol 2 retains all Protocol 1 Completion blockers and adds the following: Completion MUST NOT occur when a passed Strict Review lacks repository-native subject/Reviewer provenance; when those records do not bind to the revision under review; when either record is only `claimed`; when Reviewer and subject share an Execution or Execution Context; or when an active Protocol 2 Change attempts to use a legacy Change schema to bypass these checks.

## 9. Compatibility and evolution

Protocol 1 remains frozen with its original conceptual Reviewer/Resolver separation semantics. Protocol 2 is the first integer Protocol version in which independent Execution, independent Execution Context, revision-bound provenance, and iteration-aware re-review are normative Strict Review requirements.

Future changes that invalidate a valid Protocol 2 instance or alter the meaning of these required Gates must use a new integer Protocol identifier under C-045/C-046.
