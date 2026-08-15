---
forge:
  artifact: review
  schema: 1
change: CHG-0008
status: failed
---

# Strict Review — CHG-0008

## Verdict

**REQUEST CHANGES**

Reviewed revision: `43170fa3eb0e16d9e848c3b26e44ef757906dffc` (PR #9).

This review was executed in an independent Reviewer context and did not modify implementation code. No Resolver role was assumed in this execution.

## Verification observed

- Current HEAD GitHub Actions `Tests` run `31899799013`: PASS.
- Current HEAD `Distribution Verification` run `31899799005`: PASS.
- Historical corrected-model RED is recorded at `3d4883d0a0329a629026f22e4c314ffa04b2bfed` as `3 failed, 166 passed`.
- Historical GREEN is recorded at `fec5ac22c3ef62c213526ae3675f105a2a1afd45` as `169 passed`.

Green CI does not override the semantic findings below.

## Findings

### CHG-0008-R001 — BLOCKER — Protocol 1 compatibility contract is violated

**Affected requirements/invariants:** C-045, C-046, `protocol/compatibility.md`, FR-002, FR-014.

**Location:** `protocol/contract/engineering.md` C-026; `protocol/specification.md` §§22/25/27; `protocol/compatibility.md`; `protocol/schemas/change-v2.schema.json`.

**Failure mode:** CHG-0008 changes the normative meaning and minimum obligation of Strict Review under integer Protocol `1` from conceptual Reviewer/Resolver role separation to mandatory independent Execution and Execution Context boundaries. The compatibility policy explicitly states that a new integer Protocol identifier is required when a change invalidates a previously valid conforming Protocol 1 instance, and that when an artifact-shape change also changes Core semantic obligations, both the schema and integer Protocol version must change. Introducing only `forge/change@2` does not isolate the breaking Core semantic change because C-026 and the canonical Specification themselves are changed while Protocol remains `1`.

**Why it matters:** previously conforming Protocol 1 review executions that satisfied conceptual role separation but not the newly introduced execution/context rule become non-conforming. This is exactly the breaking boundary C-045/C-046 and `compatibility.md` prohibit.

**Required resolution:** either introduce the new Core semantics under a new integer Protocol version with an explicit migration/compatibility boundary, or demonstrate from pre-CHG-0008 canonical Protocol 1 text that execution/context independence was already normative. The current pre-change C-026 text does not support that latter interpretation.

**Evidence/reproduction:** compare PR #9 changes to C-026 and Specification §25 against `protocol/compatibility.md` section “Breaking Protocol evolution”, especially the rule that a schema suffix is insufficient when Core semantic obligations also change.

### CHG-0008-R002 — BLOCKER — Required Resolver execution/context evidence does not exist repository-natively

**Affected requirements/invariants:** C-026, Protocol Specification §§25/27, INV-001, INV-003, AC-011.

**Location:** `.forge/changes/CHG-0008-reviewer-resolver-separation/manifest.yml`, `tdd-evidence.yml`, `verification.md`, and all other CHG-0008 artifacts.

**Failure mode:** the Change intentionally remains `forge/change@1` with no `review.reviewer_identity`. No repository-native artifact records the actual implementation/Resolver `execution_id` and `context_id`. A new independent Reviewer therefore has no durable Resolver identifiers against which its own execution/context can be compared. Populating `resolver_execution_id` or `resolver_context_id` now would require retroactively inventing or reconstructing identifiers rather than recording evidence captured from the real Resolver execution.

**Why it matters:** C-026 says independence must be durably evidenced and Completion must not occur when independence cannot be demonstrated from repository-native evidence. The current Change cannot truthfully produce the complete v2 reviewer identity object without fabricating the Resolver half of that evidence.

**Required resolution:** a separate Resolver execution must define and implement a truthful provenance/capture mechanism that records implementation/Resolution execution and context identifiers at the time those executions occur, with a migration rule that does not fabricate historical evidence. CHG-0008 itself must then be resolved in a separate Resolver context and re-reviewed independently.

**Evidence/reproduction:** inspect `manifest.yml`: schema is `forge/change@1`, review is pending, and no `reviewer_identity` exists. Search the complete Change directory: no authoritative Resolver execution/context identifiers are recorded.

### CHG-0008-R003 — MAJOR — C-026 validator does not enforce the policy consistently across Flows or review states

**Affected requirements/invariants:** C-026, C-031, FR-010, FR-015, Review Policy `reviewer_resolver_separation.independence`.

**Location:** `src/forge_cli/validation/__init__.py::_validate_reviewer_resolver_separation`; `protocol/policies/review.yml`; `protocol/schemas/change-v2.schema.json`.

**Failure mode:** the validator only enters semantic C-026 checks when `flow.current` is `standard` or `full`; FAST is skipped even though Review Policy requires `execution_context` independence for FAST, STANDARD, and FULL. Separately, `forge/change@2` structurally requires `reviewer_identity` only for FULL, and `forge/change@1` permits a passed review with no identity evidence. As a result, Forge can accept states whose review status claims success while the Core-mandated independence evidence is missing or unchecked.

**Why it matters:** Core Strict Review semantics apply to every Flow. FAST reduces ceremony, not quality. A validation implementation that accepts FAST or legacy-schema `review_passed` without demonstrable independence contradicts the canonical policy and Completion rule.

**Required resolution:** enforce the Core independence requirement consistently for every Flow at the correct protocol/schema boundary, including presence requirements when review is authoritative/passed, and add regressions for FAST, STANDARD, FULL, and legacy-schema compatibility semantics.

**Evidence/reproduction:** inspect `_validate_reviewer_resolver_separation`: the flow guard is `in {"standard", "full"}`. Inspect `change-v2.schema.json`: the conditional `reviewer_identity` requirement applies only when `flow.current == full`.

### CHG-0008-R004 — MAJOR — The implementation verifies string inequality, not actual independent executions

**Affected requirements/invariants:** C-026, INV-001, FR-003, FR-004, FR-009, FR-015; adversarial case Q.

**Location:** `src/forge_cli/validation/__init__.py`; `tests/cli/test_validate.py::test_validate_accepts_independent_execution_and_context`; ADR-0008 and Architecture claims about durable/verifiable evidence.

**Failure mode:** any Resolver can construct `reviewer_identity` with arbitrary distinct strings for reviewer/resolver execution and context IDs. The validator accepts the manifest because it only checks equality. The positive regression test itself demonstrates this boundary by mutating synthetic identifiers and expecting `forge validate` success. No provenance, attestation, harness-signed reference, immutable execution record, or other mechanism ties those strings to actual independent executions.

**Why it matters:** structural validity plus unequal strings is not proof that an independent Review Execution occurred. Without an explicit trust boundary, documentation and Completion semantics can overstate what Forge mechanically verifies and allow self-issued evidence to satisfy `review_passed`.

**Required resolution:** either add a verifiable provenance/attestation mechanism that binds execution/context references to real executions, or explicitly narrow the Core/CLI guarantee to consistency checking of self-reported evidence and require an additional trustworthy evidence source before `review_passed`/Completion can be asserted. Tests must include the forged-evidence threat model rather than treating arbitrary unequal strings as sufficient proof.

**Evidence/reproduction:** create a FULL `forge/change@2` manifest with four invented, pairwise-distinct identifier strings and `review.status: passed`; current structural validation and C-026 equality checks accept it.

## TDD review

The corrected TDD-005 RED is materially useful: removing either the execution comparison or the context comparison would cause one of the two semantic regressions to fail, and reverting the v2 execution/context shape would fail the structural fixture. Compatibility coverage also protects the narrow claim that `forge/change@1` remains structurally valid.

However, regression coverage does not falsify the Core failures above: there is no FAST C-026 regression, no authoritative review-passed-without-evidence regression across schema boundaries, and no test capable of distinguishing a real independent execution from fabricated unequal identifiers.

## Review evidence boundary

This Reviewer execution is independent from the Resolver context that produced PR #9, and no implementation changes were made here. However, the schema-defined `reviewer_identity` object cannot be truthfully written because the actual Resolver `execution_id` and `context_id` were not captured in repository-native state. This review therefore deliberately does **not** fabricate `reviewer_identity` values.

A separate Resolver Execution Context is required to address these findings. This Reviewer execution stops here and must not resolve or approve its own findings.
