---
forge:
  artifact: verification
  schema: 1
change: CHG-0008
status: passed
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

## Repository-wide compatibility conflict — resolved

An earlier revision of this Change made the FULL structural requirement apply unconditionally
under the existing `forge/change@1` identifier, which broke
`test_canonical_yaml_instances_satisfy_their_declared_schemas` for every historical FULL
manifest and, self-referentially, for CHG-0008's own manifest. This Change forbids
retroactively adding fabricated evidence to historical records, and forbids this Resolver
session from fabricating its own Reviewer evidence, so neither of those was an acceptable fix.

Resolution: per `protocol/compatibility.md`'s existing schema-versioning rule ("An individual
artifact shape may instead require a new schema suffix when the break is limited to that
artifact"), the structural requirement now lives only under a new suffix, `forge/change@2`.
`forge/change@1` is restored to its original, backward-compatible shape. No Protocol version
bump was required — Protocol, Schema, CLI, and Adapter versions are independent axes.

- Historical manifests (CHG-0001, CHG-0002, CHG-0004, CHG-0006, CHG-0007) remain on
  `forge/change@1`, unmodified, and structurally valid.
- CHG-0008's own manifest remains on `forge/change@1` while its Strict Review is pending. It
  has not claimed compliance with the discipline it introduces, and truthfully cannot until a
  genuinely independent Reviewer session records real `reviewer_identity` evidence (T-014).
- The RED fixture and its structural tests declare `schema: forge/change@2` to exercise the
  new mandatory behavior; a new regression test pins the unchanged `forge/change@1` behavior so
  the two schemas cannot silently reconverge.

Independently reproduced: `pytest -q` → **168 passed, 0 failed**. `jsonschema` validation of
every `.forge/changes/CHG-*/manifest.yml` against its own declared `schema` identifier passes.

## Distribution verification

Distribution Verification remained successful on the semantic-validator implementation commit while the Tests workflow failed, confirming the observed blocker is in canonical schema/Change compatibility rather than package build/install infrastructure.

## Strict Review

PENDING EXTERNAL REVIEW. This Resolver session has not performed independent Strict Review, has not created `review.md`, has not recorded a fictional reviewer identity, and does not assert `review_passed`.

## Result

Verification **passed**. The requested semantic behavior is implemented and the compatibility
conflict is resolved via schema versioning without fabricated evidence or historical rewrites.
Full-suite GREEN, repository schema validity, and `forge validate` success are all confirmed.

This does not complete the Change. Strict Review (T-014) remains genuinely pending, performed
by nobody in this Resolver session, and `review.md` remains absent. Completion still requires
an independent Reviewer session to execute Strict Review and, if it passes, to record real
`reviewer_identity` evidence before CHG-0008 itself migrates to `forge/change@2`.
