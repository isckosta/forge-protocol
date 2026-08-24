---
forge:
  artifact: specification
  schema: 1
change: CHG-0036
status: complete
---

# Specification — CHG-0036 Merge Readiness Gate

## Summary

Introduce a read-only Merge Readiness evaluation distinct from
`forge validate`. The evaluation answers whether the current effective
revision is authorized to enter the protected branch according to the
applicable canonical Flow and repository-native evidence.

## Classification

**FULL.** The Change introduces a merge-authorization boundary, affects
Protocol/Gate semantics, CLI behavior, CI enforcement, compatibility, and
security/integrity assumptions. It requires Discovery, Specification Review,
Architecture, Test Strategy, Plan, human Plan authorization, TDD where
applicable, Verification, independent Strict Review, and Completion. An RFC
must be accepted before implementation changes Contract or canonical Gate
semantics.

## Functional Requirements

## FR-001 — Separate validation from readiness

`forge validate` MUST retain its existing validity meaning. The new readiness
surface MUST produce a distinct structured verdict and MUST NOT report
MERGE READY solely because validation passes.

## FR-002 — Deterministic revision subject

The evaluator MUST evaluate an explicit immutable `BASE..HEAD` subject. The
CLI MAY default `HEAD` to the current commit, but it MUST fail closed when
BASE, HEAD, repository root, or required history cannot be determined. CI
MUST supply the Pull Request base and head SHAs and MUST fetch complete
history. No latest/highest Change-ID heuristic is permitted.

## FR-003 — Resolve all governing Changes

The evaluator MUST resolve affected Changes from changed repository paths,
including additions, deletions, renames, malformed directories, and
contradictory manifest identities. Every materially affected Change MUST be
evaluated. Ambiguous resolution MUST block readiness.

## FR-004 — Block material changes without provenance

A centralized, repository-native materiality policy MUST identify paths and
categories that can change normative Protocol behavior, Forge runtime,
Adapter projections, executable evidence, or CI/governance enforcement. A
material diff with no governing Change MUST produce a stable provenance-missing
diagnostic. A permitted non-material diff may pass without a Change only when
the policy explicitly says so.

## FR-005 — Reuse effective Flow requirements

The evaluator MUST resolve the effective Flow through the existing Protocol
resolution mechanism and MUST derive required checks from its stages and
Gates. It MUST NOT maintain a second manual definition of FAST, STANDARD, or
FULL requirements.

## FR-006 — Recompute evidence, not claims

For each affected Change, readiness MUST verify the required artifacts and
evidence for its effective Flow, including Plan authority, TDD status or
exception, Verification, Review, Resolution, documentation, Decisions,
blocking external review threads where applicable, and Completion. Manifest
claims such as `state.current: complete` and `review.status: passed` are
inputs to consistency checks, never sufficient authorization.

## FR-007 — Plan authority must be current

For Changes subject to C-077, the evaluator MUST verify the existing human
Plan Decision and confirmation semantics and MUST additionally establish that
the authorized Plan content has not been superseded or modified. A stale,
ambiguous, malformed, self-observed, or historically unavailable approval
MUST produce a blocking diagnostic. The final representation MUST reuse or
extend canonical provenance rather than create a transient-chat authority.

## FR-008 — Verification must cover the subject

Required Verification MUST be admissible for the effective merge subject,
with required TDD evidence or justified exception, valid artifact/result
content, and no stale, superseded, malformed, or missing evidence. The
evaluator MUST inspect evidence and MUST NOT become a second test runner.

## FR-009 — Review chain and subject binding

Required Strict Review MUST have admissible Reviewer provenance, required
independence, valid iteration history, verdict, and finding state. The final
Review or Resolution Verification subject MUST bind to the effective merge
subject according to Protocol 2 frozen-subject semantics. A stale subject,
missing historical record, malformed provenance, or post-review material
change MUST block readiness.

## FR-010 — Findings and Resolution

The evaluator MUST derive blocking severity and reconciliation rules from the
canonical Review policy and existing Resolution semantics. It MUST not treat
the latest PASS as sufficient when BLOCKER or MAJOR findings remain
unreconciled, or when a required Resolution Verification and independent
re-review are absent. MINOR and OBSERVATION findings MUST follow their actual
policy treatment rather than an invented universal block.

## FR-011 — Completion is an evidenced claim

Completion MUST be accepted only when all applicable Flow completion Gates,
required artifacts, Decisions, Verification, Review/Resolution state,
revision bindings, documentation requirements, TDD requirements, and
blocking review-thread conditions are consistent. `state.current: complete`
alone MUST never produce readiness.

## FR-012 — Multiple Changes are conjunctive

When one effective diff governs multiple Changes, the verdict MUST be ready
only if every affected Change is ready. One complete Change MUST NOT mask a
second pending or blocked Change.

## FR-013 — Stable diagnostics and exit behavior

The structured result MUST be deterministic and projectable to human and
machine output. Diagnostics SHOULD use stable `MR-xxx` codes and identify
Change, Flow, expected state, actual state, artifact, and remediation. The
CLI contract MUST define exit codes as: `0` ready, `1` blocked by readiness
conditions, and `2` operational/configuration failure. Unexpected internal
errors remain subject to the CLI's existing internal-error convention.

## FR-014 — CI integration and enforcement boundary

The repository MUST provide a workflow check equivalent to
`forge-merge-readiness` that runs validation and readiness against explicit
Pull Request base/head revisions with complete history. Documentation MUST
state that this check is intended to be configured as a required protected
branch status check alongside `test` and `distribution`, with bypass disabled
where supported. The repository MUST NOT claim to configure external branch
protection itself.

## FR-015 — Preserve independent release provenance

The Merge Readiness implementation MUST remain independent from the existing
release workflow's merged-Pull-Request provenance check. Neither mechanism
may be weakened or used as a substitute for the other.

## FR-016 — Honest Harness guidance

Codex and Claude Code projections MAY instruct agents to run the readiness
check before claiming merge readiness. Such guidance MUST be labeled as
guidance and MUST NOT be represented as the enforcement mechanism.

## FR-017 — Compatibility

Protocol 1 and historical Changes that were valid under their original rules
MUST remain historically valid. The evaluator MUST define an explicit current
merge-authorization compatibility policy and MUST fail closed rather than
silently invent missing historical evidence. Existing repositories that have
not adopted the required CI check remain outside the repository's ability to
prove external enforcement.

## Acceptance Criteria

## AC-001 — Readiness is distinct

Tests demonstrate that a structurally valid Change in implementation,
verification, review, or resolution can remain blocked while `forge validate`
passes.

## AC-002 — Happy paths and lifecycle failures

FAST, STANDARD, and FULL ready fixtures pass; pending/failed Verification,
Review, Completion, unresolved BLOCKER/MAJOR, and incomplete Resolution
Verification fail with stable diagnostics.

## AC-003 — Revision and authority failures

Stale Review subjects, stale Plan authorization, unavailable history,
malformed provenance, manifest-only manipulation, and post-review material
changes fail closed.

## AC-004 — Provenance and multiple Changes

Material diff without a Change fails; permitted non-material diff can pass;
renamed/deleted/ambiguous Changes fail safely; multiple Changes require all to
pass.

## AC-005 — CI and compatibility

The workflow supplies complete history and explicit revisions, the command
returns the documented exit codes, release provenance remains independently
tested, and historical Protocol 1 behavior is not retroactively invalidated.

## AC-006 — Adversarial integrity coverage

Tests cover symlink/path confusion, shallow history, deleted artifacts,
fake or superseded Review records, changed Plan content, hidden Changes, and
differences between local and CI subject selection.

## Out of Scope

Lifecycle execution commands, a new Review/Verification engine, automatic
test execution, remote services, cryptographic attestation, GitHub branch
protection API management, release provenance replacement, and agent sandbox
enforcement are excluded.

## Non-functional Requirements

### NFR-001 — Determinism

Identical repository state and explicit revisions MUST produce identical
verdicts and diagnostic ordering.

### NFR-002 — Provider independence

Core readiness evaluation MUST remain local and provider-independent; GitHub
integration belongs only in workflow wiring and documentation.

### NFR-003 — Fail closed

Materially ambiguous authorization, provenance, history, or Change ownership
MUST never produce MERGE READY.

## Security Requirements

### SEC-001 — Assurance boundary

The implementation MUST disclose that recorded repository evidence is not
cryptographic or external proof, and MUST not claim that CI or Harness
guidance enforces external branch protection unless that configuration exists.

## Decision Record

### DEC-001 — RFC and canonical Plan binding

The RFC requirement is satisfied by accepted RFC-0006. The human decision
selected the content-digest binding alternative. Architecture must define the
exact field shape and canonicalization algorithm while preserving C-077 and
compatibility with historical Changes. This decision is resolved by explicit
human decision; implementation may not substitute a different binding.
