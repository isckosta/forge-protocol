---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0030
status: complete
---

# Test Strategy — Forge Experience Reporting

## Objective

Prove that FER is useful when explicitly enabled while the disabled path is
observationally inert for existing Forge behavior.

## Strategy

Use TDD unit tests for configuration, model validation, provenance collection,
ID allocation, atomic storage, and failure isolation; CLI tests for command
semantics; and contract/golden-path tests proving no Protocol 1/2, Flow,
Change, validate, doctor, Adapter, or Harness regression. Use temporary Git
repositories and injected storage failures for deterministic isolation.

## Required cases

1. Missing/false config is disabled; no report is created and existing CLI
   behavior/output is unchanged.
2. Enable, disable, invalid config, and repository scope are deterministic.
3. Lazy creation occurs on first material observation/positive evidence only.
4. Known provenance is populated; unknown values are not fabricated.
5. All three classifications, evidence distinctions, follow-up candidates,
   and positive-only reports round-trip as human-readable YAML.
6. Project problems are not silently rewritten as Forge problems.
7. IDs remain unique under parallel allocation and concurrent append.
8. Invalid report input, lock failure, and atomic-write failure are surfaced
   honestly without changing Change state.
9. `forge validate`, `forge doctor`, Change commands, Protocol 1/2 fixtures,
   FAST/STANDARD/FULL golden paths, and both Adapter projections remain
   unchanged when FER is disabled.

## TDD-001 — Disabled behavior

RED: a test asserts that a normal project with no contributor configuration
creates no report and that validation has no FER requirement. GREEN: implement
the default-off resolver and keep existing command paths untouched. REFACTOR:
centralize the resolver without importing it from normal validation.

## TDD-002 — Durable recording

RED: a focused test records one structured observation and expects a report,
stable observation ID, and populated safe context. GREEN: implement model,
reservation, and atomic append. REFACTOR: isolate serialization/context from
filesystem mutation.

## Completion Criteria

Focused tests, CLI tests, contract tests, golden-path tests, and the full test
suite pass; a real dogfooding report is reviewed for usefulness and contains
only actual observations; no external network or telemetry path exists.
