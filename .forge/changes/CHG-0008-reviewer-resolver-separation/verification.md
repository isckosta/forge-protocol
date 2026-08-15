---
forge:
  artifact: verification
  schema: 1
change: CHG-0008
status: failed
---

# Verification — Verifiable Reviewer/Resolver Separation

## Scope

Verification covers the Change schema, Review Policy and policy schema, C-026, Specification §25, structural/semantic validation separation, Codex projection behavior, ADR, CHANGELOG, historical Change preservation, TDD evidence, and repository-wide regression behavior.

## Valid RED evidence

The mandatory exact same-session fixture was established as structurally valid before semantic enforcement. Historical TDD-001 evidence records a test-only state where `forge validate` returned success and the new C-026 assertion failed for the expected missing-behavior reason, not because of malformed input or schema failure.

During the revised Resolver pass, commit `8a3099d5044ef802869748c02fe122a8412ed927` added the second semantic expectation for an `agent_isolated_session` claim with identical reviewer/resolver references before production support. GitHub Actions run `31852012708` failed on that test-only state. Commit `518629c8ae07f18e82dcac5fa382ffd6af8c86a5` then added the semantic identical-reference C-026 check.

Commit `7f21439e2cc4517a423f99efd1f4b0f817ca3d7e` added the structural regression requiring `reviewer_identity` even for pending FULL Review before commit `666cf96f88faaf2445ba8313ee715cad306db6c0` changed the schema to the literal revised requirement.

## Implemented behavior

- `review.reviewer_identity` is a closed object with all three inner fields required.
- FULL structurally requires the entire object solely from `flow.current == full`.
- CLI semantic validation names C-026 for FULL `agent_same_session`.
- CLI semantic validation names C-026 for a claimed independent actor whose Reviewer and Resolver session references are identical.
- Code comments/tests distinguish structural schema responsibility from semantic CLI responsibility.
- Review Policy defines FAST/ STANDARD/ FULL minimums and the explicit FULL isolated-agent fallback.
- C-026 uses the required recorded/verifiable, Flow-proportional wording.
- Codex STANDARD/FULL projection requires separate review execution and distinct session references.
- ADR documents increasing operational independence without claiming epistemic independence; `agent_different_model` remains future work only.
- CHANGELOG records the literal FULL schema requirement as breaking.
- No completed historical Change was modified, and CHG-0008 `review.md` remains absent.

## Repository-wide verification failure

The literal revised schema requirement cannot currently produce repository-wide GREEN under Protocol 1. `tests/contract/test_protocol_contract.py::test_canonical_yaml_instances_satisfy_their_declared_schemas` validates every historical `.forge/changes/*/manifest.yml` against the current schema identified as `forge/change@1`. Historical FULL manifests do not contain `reviewer_identity`, and this Change explicitly forbids retroactively adding fabricated evidence.

This is also a direct compatibility conflict with C-045/C-046: changing the same Protocol/schema identity so that previously valid conforming instances become invalid requires a new compatibility boundary. Weakening the canonical test, rewriting completed Changes, or inventing Reviewer evidence would hide rather than solve that conflict.

The CHG-0008 manifest itself is likewise FULL and has Review pending. Under the revised schema it cannot be structurally valid without a `reviewer_identity`; this Resolver session cannot truthfully supply Reviewer evidence before independent Strict Review.

## Distribution verification

Distribution Verification remained successful on the semantic-validator implementation commit while the Tests workflow failed, confirming the observed blocker is in canonical schema/Change compatibility rather than package build/install infrastructure.

## Strict Review

PENDING EXTERNAL REVIEW. This Resolver session has not performed independent Strict Review, has not created `review.md`, has not recorded a fictional reviewer identity, and does not assert `review_passed`.

## Result

Verification is **failed/blocked**, not passed. The requested semantic behavior is implemented, but CHG-0008 cannot truthfully satisfy both the literal mandatory-FULL schema requirement and the existing Protocol 1 compatibility/historical-preservation obligations. A versioning or migration decision is required before full-suite GREEN, repository schema validity, `forge validate` success, and Completion can be claimed.
