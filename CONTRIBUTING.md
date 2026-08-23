# Contributing to Forge

Forge welcomes contributions and treats changes to its Core Protocol conservatively.

## Read first

Before contributing, read `README.md`, `MANIFESTO.md`, `ARCHITECTURE.md`, `protocol/specification.md`, and `protocol/contract/engineering.md`.

## Forge develops Forge

Material Forge development uses Forge. Contributors should use the repository's `.forge/` workspace.

When deliberately dogfooding or validating Forge, contributors may opt in to
[Forge Experience Reporting](docs/experience-reporting.md) to preserve
material observations. It is disabled by default and is not part of ordinary
project use or Change validation.

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

`main` is branch-protected: direct pushes are rejected (including for administrators), and a Pull Request must merge with the `test` and `distribution` status checks passing before it can land.

Mechanically:

1. create a branch (`git checkout -b <descriptive-name>`);
2. push it and open a PR against `main`;
3. wait for `test` (`.github/workflows/tests.yml`) and `distribution` (`.github/workflows/verification.yml`) to pass — both are required checks;
4. merge once green. No second approval is required (there is no fixed reviewer roster today), but the PR itself is mandatory — it is the Change's own repository-native record of what merged and why, not a formality to skip.

PRs should explain what changed, why, the related Forge Change or RFC, TDD evidence when applicable, Verification performed, and Documentation Impact.

## Review

Forge uses adversarial Review. Passing tests do not eliminate the need for engineering judgment.

## AI-assisted contributions

AI-assisted contributions are allowed. The contributor remains responsible for the submitted Change. Generated code receives no reduced review standard.

## Releasing

See `RELEASING.md` for the version scheme and release checklist. Not a contributor-facing process; documented here only as a pointer.
