---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0035
status: pending
---

# Test Strategy — CHG-0035 Automatic Material Observation Capture

## Objective

Prove that policy-driven capture reduces loss of mechanically observable Forge
evidence without turning FER into logging, changing normative Forge behavior,
or weakening existing FER safety and compatibility guarantees.

## Strategy

Use unit tests for event normalization, allowlisting, classification,
fingerprints, and sanitization; storage integration tests for deduplication,
optional fields, Markdown, and failure isolation; CLI/Adapter tests for the
real producer boundary; and regression tests for disabled FER, manual capture,
historical reports, and `forge validate`.

## TDD-001 — Disabled path

With absent/false configuration, submit a supported event and assert no report,
Markdown, fingerprint file, or auxiliary state exists.

## TDD-002 — Accepted Forge event

Submit a named Adapter conformance event with FER enabled and assert one
`uncertain` observation, `capture.mode: automatic`, detector provenance, and
consistent YAML/Markdown output.

## TDD-003 — Ordinary failures ignored

Submit project/test failure, generic exception, non-zero exit, and unlisted
validation events; assert policy returns `IGNORE` and storage is untouched.

## TDD-004 — Deduplication and distinction

Capture the same stable event repeatedly and assert one observation. Change
expected or observed stable content and assert a second observation.

## TDD-005 — Isolation and privacy

Inject policy/storage failure and assert the producer result is unchanged.
Submit oversized, secret-looking, raw-log, and unbounded evidence and assert
rejection before persistence.

## TDD-006 — Compatibility and manual path

Validate existing FER YAML/Markdown fixtures, append automatic and manual
entries, render projections, and assert existing `forge experience record`
behavior remains unchanged.

## TDD-007 — Non-normative boundaries

Run `forge validate` and Adapter conformance with automatic capture enabled and
assert FER contents do not alter validity, lifecycle, Gate, or Adapter result.

## Non-mechanical Validation

Review the allowlist and responsibility documentation for absence of lifecycle
claims, event-log behavior, automatic root-cause classification, and sensitive
data capture. Inspect generated YAML/Markdown for bounded evidence.

## Completion Criteria

All focused tests, contract tests, Adapter tests, `forge validate`, FER
validation, Markdown rendering, and the full suite pass; documentation and
Change artifacts accurately record the final behavior.
