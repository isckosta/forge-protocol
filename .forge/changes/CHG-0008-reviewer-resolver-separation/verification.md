---
forge:
  artifact: verification
  schema: 1
change: CHG-0008
status: active
---

# Verification — Verifiable Reviewer/Resolver Separation

## Scope

Verification covers the Change schema, Review Policy and its schema, C-026, Specification §25, CLI semantic validation, Codex projection behavior, ADR, CHANGELOG, historical Change preservation, and TDD evidence.

## Durable RED evidence

Commit `1f83d498124d028fccf8ae3a01bd18a1d068a758` contains the test before production validation behavior. GitHub Actions run `31851211926` completed with `1 failed, 162 passed`. The sole failure was `test_validate_rejects_full_change_reviewed_in_same_session`: expected CLI exit code 2, actual exit code 0. This is the expected missing-behavior failure and not a fixture, syntax, dependency, or environment failure.

## Intermediate GREEN/remediation

Commit `21711a79c0ffe69ae2a2bbc18ad41bfb48f3b1fd` implemented the semantic validator and Codex projection behavior. The behavioral target became green, but the full suite exposed contract-schema fallout: completed historical FULL manifests lacked the new field and `policy-review.schema.json` still required the old boolean policy shape. No historical manifests were modified. Remediation updates the policy schema and preserves completed records while enforcing identity prospectively for actual active FULL review execution.

## Final automated verification

Pending the fresh post-artifact CI run. This document must be updated with the final commit/run and test counts before external Strict Review.

## Documentation verification

ADR-0008 explicitly limits the guarantee of same-model isolated sessions to reduced context contamination and states that correlated model bias remains. `agent_different_model` is future work only. CHANGELOG records the evolution as breaking.

## Strict Review

PENDING EXTERNAL REVIEW. This Resolver session has not performed independent Strict Review, has not created `review.md`, and does not assert `review_passed`.
