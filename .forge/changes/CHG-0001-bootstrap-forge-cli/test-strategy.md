---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0001
status: active
---

# Test Strategy — Bootstrap Forge CLI

## Objective

Drive all reasonably testable CLI behavior through TDD and provide independent Verification of the resulting package.

## Principles

Tests validate observable behavior. Tests must not merely mirror Implementation structure. RED must be executed and observed before corresponding production behavior. Post-hoc tests do not count as TDD evidence.

## Test levels

### Unit
Use for isolated deterministic behavior such as Protocol version compatibility, configuration interpretation, validation rules, error mapping, and path resolution.

### Integration
Use temporary Git repositories for `forge init`, `forge validate`, `forge doctor`, workspace preservation, nested Project Root resolution, and generated file validation.

### CLI
Exercise the public Typer application for externally visible behavior.

## First TDD cycle

The first production behavior will be FR-003 `forge version`.

Before production code exists:
1. bootstrap test infrastructure;
2. create a CLI behavior test for `forge version`;
3. execute it;
4. observe a valid behavioral RED;
5. record concise RED evidence;
6. implement minimum GREEN;
7. re-run the test;
8. refactor only after GREEN.

## Requirement strategy

- FR-001/FR-002: unit and integration tests around Git root resolution.
- FR-003: CLI behavior test.
- FR-004..FR-015: integration tests using temporary Git repositories and configuration fixtures.
- FR-016..FR-023: unit/integration validation tests against valid and invalid fixtures.
- FR-024..FR-027: read-only Doctor integration tests.
- FR-028: CLI surface test asserting lifecycle commands are absent.
- FR-029..FR-032: CLI exit-code tests.

## Bugfix policy

Any defect discovered during CHG-0001 must first receive a regression test reproducing it when reasonably automatable.

## RED evidence

For each behavioral cycle, retain concise evidence containing related Requirement, test identifier, expected failure, and observed failure reason. Full logs are not required unless useful for diagnosis.

## GREEN evidence

The previously failing test passes and relevant existing tests remain passing.

## Refactoring

Refactoring occurs only after GREEN. New behavior discovered during refactoring requires another RED cycle.

## Verification beyond TDD

Completion Verification also includes full test suite, package installation smoke test, Schema validation, dependency inspection, offline-operation verification, static analysis/type checks when configured, and supported Python version checks where practical.
