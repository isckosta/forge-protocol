---
forge:
  artifact: review
  schema: 1
change: CHG-0008
status: failed
---

# Strict Review — CHG-0008

## Strict Review Iteration 1

### Verdict

**REQUEST CHANGES**

Reviewed revision: `43170fa3eb0e16d9e848c3b26e44ef757906dffc` (PR #9).

This review was executed in an independent Reviewer context and did not modify implementation code. No Resolver role was assumed in this execution.

### Verification observed

- Current HEAD GitHub Actions `Tests` run `31899799013`: PASS.
- Current HEAD `Distribution Verification` run `31899799005`: PASS.
- Historical corrected-model RED is recorded at `3d4883d0a0329a629026f22e4c314ffa04b2bfed` as `3 failed, 166 passed`.
- Historical GREEN is recorded at `fec5ac22c3ef62c213526ae3675f105a2a1afd45` as `169 passed`.

Green CI does not override the semantic findings below.

### Findings

#### CHG-0008-R001 — BLOCKER — Protocol 1 compatibility contract is violated

**Affected requirements/invariants:** C-045, C-046, `protocol/compatibility.md`, FR-002, FR-014.

**Location:** `protocol/contract/engineering.md` C-026; `protocol/specification.md` §§22/25/27; `protocol/compatibility.md`; `protocol/schemas/change-v2.schema.json`.

**Failure mode:** CHG-0008 changes the normative meaning and minimum obligation of Strict Review under integer Protocol `1` from conceptual Reviewer/Resolver role separation to mandatory independent Execution and Execution Context boundaries. The compatibility policy explicitly states that a new integer Protocol identifier is required when a change invalidates a previously valid conforming Protocol 1 instance, and that when an artifact-shape change also changes Core semantic obligations, both the schema and integer Protocol version must change. Introducing only `forge/change@2` does not isolate the breaking Core semantic change because C-026 and the canonical Specification themselves are changed while Protocol remains `1`.

**Why it matters:** previously conforming Protocol 1 review executions that satisfied conceptual role separation but not the newly introduced execution/context rule become non-conforming. This is exactly the breaking boundary C-045/C-046 and `compatibility.md` prohibit.

**Required resolution:** either introduce the new Core semantics under a new integer Protocol version with an explicit migration/compatibility boundary, or demonstrate from pre-CHG-0008 canonical Protocol 1 text that execution/context independence was already normative. The current pre-change C-026 text does not support that latter interpretation.

**Evidence/reproduction:** compare PR #9 changes to C-026 and Specification §25 against `protocol/compatibility.md` section “Breaking Protocol evolution”, especially the rule that a schema suffix is insufficient when Core semantic obligations also change.

#### CHG-0008-R002 — BLOCKER — Required Resolver execution/context evidence does not exist repository-natively

**Affected requirements/invariants:** C-026, Protocol Specification §§25/27, INV-001, INV-003, AC-011.

**Location:** `.forge/changes/CHG-0008-reviewer-resolver-separation/manifest.yml`, `tdd-evidence.yml`, `verification.md`, and all other CHG-0008 artifacts.

**Failure mode:** the Change intentionally remains `forge/change@1` with no `review.reviewer_identity`. No repository-native artifact records the actual implementation/Resolver `execution_id` and `context_id`. A new independent Reviewer therefore has no durable Resolver identifiers against which its own execution/context can be compared. Populating `resolver_execution_id` or `resolver_context_id` now would require retroactively inventing or reconstructing identifiers rather than recording evidence captured from the real Resolver execution.

**Why it matters:** C-026 says independence must be durably evidenced and Completion must not occur when independence cannot be demonstrated from repository-native evidence. The current Change cannot truthfully produce the complete v2 reviewer identity object without fabricating the Resolver half of that evidence.

**Required resolution:** a separate Resolver execution must define and implement a truthful provenance/capture mechanism that records implementation/Resolution execution and context identifiers at the time those executions occur, with a migration rule that does not fabricate historical evidence. CHG-0008 itself must then be resolved in a separate Resolver context and re-reviewed independently.

**Evidence/reproduction:** inspect `manifest.yml`: schema is `forge/change@1`, review is pending, and no `reviewer_identity` exists. Search the complete Change directory: no authoritative Resolver execution/context identifiers are recorded.

#### CHG-0008-R003 — MAJOR — C-026 validator does not enforce the policy consistently across Flows or review states

**Affected requirements/invariants:** C-026, C-031, FR-010, FR-015, Review Policy `reviewer_resolver_separation.independence`.

**Location:** `src/forge_cli/validation/__init__.py::_validate_reviewer_resolver_separation`; `protocol/policies/review.yml`; `protocol/schemas/change-v2.schema.json`.

**Failure mode:** the validator only enters semantic C-026 checks when `flow.current` is `standard` or `full`; FAST is skipped even though Review Policy requires `execution_context` independence for FAST, STANDARD, and FULL. Separately, `forge/change@2` structurally requires `reviewer_identity` only for FULL, and `forge/change@1` permits a passed review with no identity evidence. As a result, Forge can accept states whose review status claims success while the Core-mandated independence evidence is missing or unchecked.

**Why it matters:** Core Strict Review semantics apply to every Flow. FAST reduces ceremony, not quality. A validation implementation that accepts FAST or legacy-schema `review_passed` without demonstrable independence contradicts the canonical policy and Completion rule.

**Required resolution:** enforce the Core independence requirement consistently for every Flow at the correct protocol/schema boundary, including presence requirements when review is authoritative/passed, and add regressions for FAST, STANDARD, FULL, and legacy-schema compatibility semantics.

**Evidence/reproduction:** inspect `_validate_reviewer_resolver_separation`: the flow guard is `in {"standard", "full"}`. Inspect `change-v2.schema.json`: the conditional `reviewer_identity` requirement applies only when `flow.current == full`.

#### CHG-0008-R004 — MAJOR — The implementation verifies string inequality, not actual independent executions

**Affected requirements/invariants:** C-026, INV-001, FR-003, FR-004, FR-009, FR-015; adversarial case Q.

**Location:** `src/forge_cli/validation/__init__.py`; `tests/cli/test_validate.py::test_validate_accepts_independent_execution_and_context`; ADR-0008 and Architecture claims about durable/verifiable evidence.

**Failure mode:** any Resolver can construct `reviewer_identity` with arbitrary distinct strings for reviewer/resolver execution and context IDs. The validator accepts the manifest because it only checks equality. The positive regression test itself demonstrates this boundary by mutating synthetic identifiers and expecting `forge validate` success. No provenance, attestation, harness-signed reference, immutable execution record, or other mechanism ties those strings to actual independent executions.

**Why it matters:** structural validity plus unequal strings is not proof that an independent Review Execution occurred. Without an explicit trust boundary, documentation and Completion semantics can overstate what Forge mechanically verifies and allow self-issued evidence to satisfy `review_passed`.

**Required resolution:** either add a verifiable provenance/attestation mechanism that binds execution/context references to real executions, or explicitly narrow the Core/CLI guarantee to consistency checking of self-reported evidence and require an additional trustworthy evidence source before `review_passed`/Completion can be asserted. Tests must include the forged-evidence threat model rather than treating arbitrary unequal strings as sufficient proof.

**Evidence/reproduction:** create a FULL `forge/change@2` manifest with four invented, pairwise-distinct identifier strings and `review.status: passed`; current structural validation and C-026 equality checks accept it.

### TDD review

The corrected TDD-005 RED is materially useful: removing either the execution comparison or the context comparison would cause one of the two semantic regressions to fail, and reverting the v2 execution/context shape would fail the structural fixture. Compatibility coverage also protects the narrow claim that `forge/change@1` remains structurally valid.

However, regression coverage does not falsify the Core failures above: there is no FAST C-026 regression, no authoritative review-passed-without-evidence regression across schema boundaries, and no test capable of distinguishing a real independent execution from fabricated unequal identifiers.

### Review evidence boundary

This Reviewer execution is independent from the Resolver context that produced PR #9, and no implementation changes were made here. However, the schema-defined `reviewer_identity` object cannot be truthfully written because the actual Resolver `execution_id` and `context_id` were not captured in repository-native state. This review therefore deliberately does **not** fabricate `reviewer_identity` values.

A separate Resolver Execution Context is required to address these findings. This Reviewer execution stops here and must not resolve or approve its own findings.

---

## Strict Review Iteration 2

### Verdict

**REQUEST CHANGES**

Subject HEAD reviewed: `f5a825917170ac684fefaa2b096a7ff83996d5cd` on PR #9, branch `feat/chg-0008-reviewer-resolver-separation`.

Applicable Protocol: `2`.

Reviewer provenance: `review-002`, Execution `review-exec-chg0008-20260815-02`, Execution Context `review-context-chg0008-20260815-02`, assurance `recorded`, observed by `self`. No provider-native execution/context ID or external attestation was available, so this review does not claim `verified` assurance.

Subject provenance: `resolution-001`, Execution `resolution-exec-chg0008-20260815-01`, Execution Context `resolution-context-chg0008-20260815-01`, assurance `recorded`, observed by `self`.

The Reviewer Execution and Context are distinct from the subject Execution and Context. This establishes the repository-native separation required at the `recorded` assurance level, but does not constitute cryptographic or externally attested proof.

### Verification observed

- GitHub Actions at subject HEAD `f5a825917170ac684fefaa2b096a7ff83996d5cd`: `Tests` run `31901504427` PASS.
- GitHub Actions at subject HEAD: `Distribution Verification` run `31901504537` PASS.
- Local repository execution was not possible in this Reviewer runtime because outbound DNS/network cloning of `github.com` is blocked. Source, tests, schemas, canonical resources, PR diff, commits, and CI were inspected through the repository-native GitHub connector.
- Resolution TDD evidence records RED `d71435f9b2fca5c5829121ff45e0059e67526d84` and GREEN `538a77dcd77aed0db0505a288fc1cbea0e69def3` with `182 passed in 3.83s`.
- Current regression coverage exercises FAST/STANDARD/FULL, missing provenance, nonexistent references, wrong revision ID, shared Execution, shared Context, partial records, re-review contamination, active schema downgrade, Protocol 1 compatibility, and valid independent provenance.
- No regression was found that makes `revision.commit` disagree while keeping `revision.id` equal; the validator does not read `revision.commit` when enforcing C-026.

### Iteration 1 finding re-evaluation

#### CHG-0008-R001 — RESOLVED

Protocol 1 semantic meaning is explicitly frozen. Protocol 2 has integer identifier `2`; the stronger C-026 obligation lives under `protocol/versions/2/`; `forge/change@2` is an artifact shape rather than a substitute for Protocol versioning; active Protocol 2 Changes cannot downgrade to `forge/change@1`; completed historical Protocol 1 Changes remain permitted without retroactive provenance. The compatibility document and Protocol 2 Contract preserve C-045/C-046 as the version boundary.

#### CHG-0008-R002 — RESOLVED

`provenance.yml` now contains prospective repository-native `resolution-001` provenance with Role, Execution, Execution Context, capture time, logical revision, commit, source and assurance. `review-002.subject_provenance` resolves to that record. No Implementation or Iteration 1 provenance was fabricated; the historical absence remains explicit.

#### CHG-0008-R003 — RESOLVED

Protocol 2 validation is applied project-wide and the passed-review gate does not branch by Flow. Regression tests explicitly parameterize FAST, STANDARD and FULL for both missing provenance rejection and valid provenance acceptance. Protocol 1 projects bypass the Protocol 2 C-026 gate, preserving the historical semantic boundary. Pending/failed reviews do not assert `review_passed`; Completion with a passed Protocol 2 review remains subject to the same validator.

#### CHG-0008-R004 — PARTIALLY RESOLVED

The original arbitrary-string vulnerability is materially reduced: passed iterations must resolve `subject_provenance` and `reviewer_provenance` to real ledger records, Role and assurance are checked, claimed provenance is insufficient, revision IDs must match, and shared Execution/Context is rejected. Documentation also correctly states that `recorded` is self-recorded repository evidence rather than cryptographic/external proof.

However, the forged-evidence boundary is not fully closed because the validator ignores the optional-but-present `revision.commit`. A record can carry the expected logical revision ID while binding to a different commit, and C-026 validation still accepts it. This violates the claimed revision-bound evidence model when commit information is available.

### New finding

#### CHG-0008-R005 — MAJOR — Commit binding is recorded but not enforced

**Affected requirements/invariants:** Protocol 2 Specification §§3, 5 and 8; C-026; Review Policy `revision_binding_required`; FR-004/FR-009/FR-015 as represented by the Resolution; repository-authority semantics.

**Location:** `src/forge_cli/validation/__init__.py::_record_fields` and `_validate_protocol2_review_provenance`; `protocol/schemas/execution-provenance.schema.json`; `tests/cli/test_validate.py`; `.forge/changes/CHG-0008-reviewer-resolver-separation/provenance.yml`.

**Failure mode:** provenance schema permits `revision.commit`, and CHG-0008 records it, but `_record_fields` returns only `revision.id`; C-026 validation compares only that logical ID. Two records with the same `revision.id` and different commit SHAs therefore satisfy the mechanical revision-linkage check. The current Change demonstrates the ambiguity directly: `resolution-001` binds `chg-0008-resolution-001` to `538a77dcd77aed0db0505a288fc1cbea0e69def3`, while the actual subject HEAD reviewed after the Resolver's final evidence commit is `f5a825917170ac684fefaa2b096a7ff83996d5cd`.

**Impact:** Protocol 2 can report a passed Strict Review for a logical revision whose subject and Reviewer records identify different concrete commits. This weakens repository-native provenance exactly at the revision boundary the Change is intended to make auditable and permits commit-level evidence substitution.

**Reproduction/evidence:** construct otherwise valid subject and Reviewer provenance with identical `revision.id`, independent Execution/Context, `recorded` assurance, but different 40-character `revision.commit` values. The current validator never reads or compares those commit values. Existing tests use matching synthetic commits and contain no mismatch regression.

**Required resolution:** when commit binding is present/applicable, Core must validate it consistently with the reviewed revision and across subject/Reviewer provenance; the Resolution provenance for the revision actually submitted to re-review must identify the concrete subject commit. Add a valid RED that changes only commit binding, then GREEN enforcement. Preserve Protocol 1 compatibility and the `recorded`/`verified` trust distinction.

### TDD audit — Iteration 2

TDD-006 is credible evidence for the broad R001-R004 Resolution because its RED occurs before the consolidated GREEN and the CI metadata shows environment/setup succeeded before the test failure. TDD-007 separately covers Protocol-aware Adapter projection. The current suite is materially stronger than Iteration 1 and would detect several key regressions.

TDD evidence is nevertheless incomplete for the commit-binding behavior now claimed by the provenance model. TDD-006 describes “revision-bound” provenance but the implemented tests establish logical revision-ID equality only; no RED/GREEN cycle demonstrates commit mismatch rejection. That gap supports R005 and prevents PASS.

### Final Iteration 2 conclusion

R001: **RESOLVED**.

R002: **RESOLVED**.

R003: **RESOLVED**.

R004: **PARTIALLY RESOLVED**.

New finding: **CHG-0008-R005 — MAJOR**.

Strict Review Iteration 2 therefore fails with **REQUEST CHANGES**. CHG-0008 remains in `strict_review`. A new independent Resolution Execution is required; this Reviewer execution must not implement that Resolution or approve its own finding.

---

## Strict Review Iteration 3

### Verdict

**REQUEST CHANGES**

PR HEAD observed before Reviewer-owned metadata commits: `48b4cacaf48c2b7db9e01d10ea5051cf92663083`.

Frozen Resolution 2 subject: `8642bb607a276139e91ec4030b7fb0a18ca1023b`.

Logical revision: `chg-0008-resolution-002`.

Reviewer provenance: `review-003`, Execution `review-exec-chg0008-20260815-03`, Execution Context `review-context-chg0008-20260815-03`, assurance `recorded`, observed by `self`.

Subject provenance: `resolution-002`, Execution `resolution-exec-chg0008-20260815-02`, Execution Context `resolution-context-chg0008-20260815-02`, assurance `recorded`, observed by `self`.

The Reviewer Execution and Context are distinct from the Resolution 2 Execution and Context. Both provenance records bind to logical revision `chg-0008-resolution-002` and immutable Git revision `8642bb607a276139e91ec4030b7fb0a18ca1023b`.

### Review-subject freeze

The frozen subject is an ancestor of the observed PR HEAD. Exactly two commits followed it before this Review began:

- `f0a5144aac4a629177a3f564982783a1236d2511` changed only `.forge/changes/CHG-0008-reviewer-resolver-separation/provenance.yml`.
- `48b4cacaf48c2b7db9e01d10ea5051cf92663083` changed only `.forge/changes/CHG-0008-reviewer-resolver-separation/manifest.yml`.

Those paths are within the narrow review-control metadata exception. No post-freeze committed change to source, tests, schemas, normative Protocol resources, Verification, Architecture, Specification, Test Strategy, or other review-subject content was observed before the Reviewer-owned metadata commits.

### R004 / R005 re-evaluation

**CHG-0008-R004 — RESOLVED for concrete committed revision substitution.** Passed Protocol 2 iterations now resolve both subject and Reviewer provenance, validate roles/assurance/logical revision, compare normalized immutable revision tuples, and reject shared Execution/Context. A same logical revision with different immutable Git commits is mechanically rejected.

**CHG-0008-R005 — RESOLVED for subject/reviewer immutable binding and commit/immutable_ref consistency.** `git_commit` immutable refs are normalized as 40-hex values; when `revision.commit` is also present it must match the immutable ref. The dedicated TDD-008 cycle records a causal RED for the prior logical-ID-only behavior and a GREEN after concrete binding enforcement.

### New finding

#### CHG-0008-R006 — MAJOR — Review-subject freeze ignores uncommitted, staged, and untracked subject mutation

**Location:** `src/forge_cli/validation/__init__.py::_changed`; `tests/cli/test_revision_binding.py`.

**Observed behavior:** `_changed` executes only `git diff --name-only <frozen_commit>..HEAD` and subtracts the three allowed review-control metadata paths. This comparison sees committed changes between the frozen commit and `HEAD`, but it does not inspect the working tree, index/staging area, or untracked files. The regression suite covers a post-freeze mutation only after committing it; it has no dirty-working-tree, staged-only, or untracked-file freeze regression.

**Expected behavior:** Protocol 2 Review Policy states `post_freeze_subject_mutation_invalidates_binding: true`. A frozen review subject must therefore be rejected when reviewable source/spec/test/evidence content has mutated after the freeze even if that mutation has not yet become a commit. Review-control metadata must remain the only narrow exception.

**Evidence/reproduction:** freeze subject commit A and record explicit `git_commit` provenance for A; then modify a reviewable tracked file without committing, or stage that change without committing, or create an untracked reviewable file; run `forge validate`. Because `HEAD` remains A (or contains only allowed review-control metadata commits), `git diff A..HEAD` reports no forbidden path and the validator can accept stale subject provenance despite the checkout no longer matching the frozen subject.

**Affected requirements/constraints:** C-026 concrete review-subject binding; Protocol 2 Review Policy `review_subject_freeze_required` and `post_freeze_subject_mutation_invalidates_binding`; local-first repository authority; adversarial stale-provenance requirement.

**Impact:** Strict Review can be marked passed against an immutable commit while the actual local material presented to the Reviewer differs from that commit. This breaks the central stale-provenance guarantee and creates different validation semantics for committed versus uncommitted mutations of the same subject content.

### Verification observed

- Tests workflow at observed HEAD: run `31903363688`, job `95057400911`, PASS at `48b4cacaf48c2b7db9e01d10ea5051cf92663083`.
- Distribution Verification at observed HEAD: run `31903363768`, job `95057401295`, PASS. Wheel build, isolated wheel-only install, offline CLI version, offline `init -> validate -> doctor`, isolated Adapter schema/loader probe, and runtime dependency audit all passed.
- Local `pytest -q`, `forge validate`, and `forge doctor` could not be executed in this Reviewer runtime because no repository checkout is mounted and outbound GitHub DNS/clone access is blocked. The current GitHub Actions workflows are therefore the executable evidence for the observed HEAD.
- The green suite does not falsify R006 because `tests/cli/test_revision_binding.py` tests committed post-freeze mutation, not working-tree/index/untracked mutation.

### Compatibility and Flow assessment

Protocol 1 compatibility remains preserved by the Protocol-aware validation boundary; Protocol 1 does not retroactively require Protocol 2 provenance or immutable review subjects.

Protocol 2 FAST, STANDARD, and FULL share the same provenance validation path, and the regression suite parameterizes all three Flows for valid immutable binding. No Flow-specific bypass was identified in the committed-revision checks. R006 applies equally to all Protocol 2 Flows because the working-tree blind spot is below the Flow boundary.

### Final Iteration 3 conclusion

R004: **RESOLVED**.

R005: **RESOLVED**.

New finding: **CHG-0008-R006 — MAJOR**.

Strict Review Iteration 3 therefore fails with **REQUEST CHANGES**. CHG-0008 remains in `strict_review`. A new independent Resolver execution must address R006; this Reviewer execution must not implement that Resolution or approve its own finding.
