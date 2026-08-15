---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0008
status: approved
---

# Test Strategy — Verifiable Reviewer/Resolver Separation

## TDD targets

The mandatory behavioral RED uses `tests/fixtures/full-change-agent-same-session.yml` exactly as specified: `actor_type: agent_same_session`, `session_ref: resolver-session`, and `resolver_session_ref: resolver-session`. A dedicated structural assertion first validates this fixture successfully against `change.schema.json`; the CLI test then requires `forge validate` to exit 2 and name C-026.

A second semantic regression mutates only `actor_type` to `agent_isolated_session` while retaining identical session references. It remains structurally valid and MUST fail `forge validate` with C-026 because the claimed isolation is inconsistent with the evidence.

A structural regression removes `reviewer_identity` from a FULL manifest whose Review is still `pending`. JSON Schema MUST reject it, proving the FULL requirement does not depend on Review status.

## RED validity

A valid semantic RED must fail at the behavioral assertion because the pre-change CLI validator accepts the structurally valid fixture. Schema errors, malformed YAML, fixture errors, import failures, dependency failures, and unrelated environment failures do not count as RED per C-011.

The original exact-fixture RED is durably recorded by the test-only commit and failing GitHub Actions run. The additional identical-reference semantic case was also introduced before its production check and produced a failing CI run.

## GREEN

Implement only the semantic C-026 checks missing from the CLI validator while leaving structural presence/type enforcement to JSON Schema. Re-run targeted CLI tests and the complete suite.

## Regression coverage

- JSON Schema tests distinguish structural failure from semantic C-026 failure.
- Contract tests validate canonical YAML instances against their declared schemas.
- Review Policy schema coverage protects the Flow-proportional policy shape.
- Codex unit coverage asserts STANDARD/FULL generated instructions contain isolated-review and distinct-session-reference requirements.
- Distribution Verification protects packaged/offline behavior.
- Full `pytest -q` protects unrelated CLI, Adapter, schema, and integration behavior.

## Expected compatibility signal

The literal revised FULL schema requirement is expected to make canonical-instance validation fail for historical FULL `forge/change@1` manifests that cannot be retroactively edited under the Change's non-goals. That failure is not to be suppressed or reclassified as success; it is evidence of the unresolved C-045/C-046 versioning conflict.

## Manual/document review

Verify exact C-026 wording, Specification §25 alignment, ADR operational-versus-epistemic language, CHANGELOG breaking note, and absence of `review.md` for CHG-0008.
