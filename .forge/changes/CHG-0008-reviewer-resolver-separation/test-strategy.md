---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0008
status: approved
---

# Test Strategy — Verifiable Reviewer/Resolver Separation

## TDD target

FR-006 is the mandatory behavioral TDD target. The test creates a valid Forge project containing a FULL Change fixture whose `reviewer_identity.actor_type` is `agent_same_session`, runs `forge validate`, and requires exit code 2 plus C-026 in output.

## RED validity

The RED test must fail because the existing validator returns success, not because of malformed YAML, fixture setup, imports, schema failure, or environment failure. Durable evidence is the test-only commit and its GitHub Actions run.

## GREEN

Implement the smallest semantic validator that discovers Change manifests and rejects the prohibited FULL actor type. Re-run the full suite.

## Regression coverage

- Contract tests validate canonical YAML against schemas, including the new Review Policy shape and historical Change compatibility.
- Codex unit coverage asserts STANDARD/FULL generated instructions contain isolated-review and session-reference requirements.
- Distribution Verification confirms packaged resources remain valid offline.
- Full `pytest -q` protects unrelated CLI, Adapter, schema, and integration behavior.

## Manual/document review

Verify C-026, Specification §25, ADR language, CHANGELOG breaking note, and absence of `review.md` for CHG-0008.
