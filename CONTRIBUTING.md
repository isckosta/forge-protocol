# Contributing to Forge

Forge welcomes contributions and treats changes to its Core Protocol conservatively.

## Read first

Before contributing, read `README.md`, `MANIFESTO.md`, `ARCHITECTURE.md`, `protocol/specification.md`, and `protocol/contract/engineering.md`.

## Forge develops Forge

Material Forge development uses Forge. Contributors should use the repository's `.forge/` workspace.

## TDD-first contributions

Reasonably testable behavioral Changes must use TDD:

1. identify behavior;
2. create the relevant test;
3. execute and observe valid RED;
4. implement minimum GREEN;
5. refactor while preserving GREEN;
6. perform broader Verification.

A test added after implementation does not count as TDD evidence.

## Bugfixes

Reasonably reproducible defects should first receive a regression test demonstrating the defect before the fix.

## RFC requirement

Create an RFC before materially changing Change semantics, canonical Flows, the Engineering Contract, TDD semantics, Gate semantics, Review semantics, persistence, Harness Conformance, configuration resolution, or Protocol interoperability.

## ADR requirement

Use ADRs for long-lived internal Architecture Decisions.

## Pull Requests

PRs should explain what changed, why, the related Forge Change or RFC, TDD evidence when applicable, Verification performed, and Documentation Impact.

## Review

Forge uses adversarial Review. Passing tests do not eliminate the need for engineering judgment.

## AI-assisted contributions

AI-assisted contributions are allowed. The contributor remains responsible for the submitted Change. Generated code receives no reduced review standard.
