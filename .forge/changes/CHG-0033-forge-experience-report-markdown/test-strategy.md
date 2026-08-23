---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0033
status: complete
---

# Test Strategy — CHG-0033 Forge Experience Report Markdown

## Objective

Prove Markdown is a faithful, deterministic, safe projection of canonical FER
data and that synchronization preserves default-off and failure-isolated
behavior.

## Strategy

Use TDD for a pure renderer first, then storage integration, then CLI and
historical migration. Assert complete output strings for representative
fixtures and targeted invariants for optional fields, escaping, ordering, and
failure states. Run existing FER, CLI, contract, Adapter, and full suites.

## Required Cases

1. Complete report renders ID, context, summary, complete observation, positive
   evidence, and follow-up candidate.
2. Missing optional fields and empty lists omit false values and empty sections.
3. IDs, source values, multiline text, paths, and links retain exact content;
   user text cannot create Markdown structure.
4. Array ordering is canonical and stable; same input is byte-identical.
5. First record creates YAML and Markdown; append updates both.
6. Existing YAML-only report renders; `--all` covers historical reports.
7. Manual Markdown edit is repaired; canonical YAML is unchanged by rendering.
8. Projection failure is explicit and canonical YAML remains valid.
9. Missing/false FER configuration and normal `forge validate` are unaffected.

## TDD Cycles

### TDD-001 — Pure deterministic projection

RED: assert expected Markdown before renderer exists. GREEN: add minimal pure
renderer. REFACTOR: isolate escaping and section helpers without output drift.

### TDD-002 — Official write synchronization

RED: assert record creates/updates Markdown and simulated projection failure
leaves canonical YAML valid. GREEN: integrate into locked storage. REFACTOR:
keep serialization and replacement helpers focused.

### TDD-003 — Explicit regeneration

RED: assert `render` creates missing Markdown and repairs drift. GREEN: add
one-report and `--all` handling. REFACTOR: share canonical loading/diagnostics.

## Completion Criteria

Focused and existing suites pass; disabled-path tests pass; `render --all` is
idempotent; generated fixtures are reviewed; unrelated baseline failures are
recorded honestly.
