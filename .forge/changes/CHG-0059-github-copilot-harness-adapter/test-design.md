---
forge:
  artifact: test_design
  schema: 1
change: CHG-0059
status: complete
---

# CHG-0059 · Test Design

> Verification Design

## Test Strategy

Use unit tests for descriptor, registry, deterministic projection, publication
target, and hook behavior; use existing adapter distribution and CLI tests for
packaging and registry integration. A real Copilot session is not required for
the repository projection contract and is not claimed as automated evidence.

| Layer | Scope | Method |
|---|---|---|
| Layer A | Adapter projection and hooks | Automated |
| Layer B | Adapter distribution and CLI registry | Automated |

## Coverage Map

| Requirement | Scenario | Method |
|---|---|---|
| FR-001 | TD-001, TD-005 | Automated |
| FR-002 | TD-002 | Automated |
| FR-003 | TD-002 | Automated |
| FR-004 | TD-003, TD-004 | Automated |
| FR-005 | TD-005 | Automated |

## Layer A · Adapter projection and hooks

### TD-001 · Packaged descriptor and evidence
Requirements: FR-001
Type: Unit
Priority: required

#### Purpose
Proves that the Adapter can be discovered offline with dated vendor evidence
and a Protocol-compatible manifest.

#### Scenario
Given packaged Adapter resources
When the descriptor is loaded
Then manifest and evidence are valid.

#### Evidence
Pytest result and descriptor values.

#### Failure Condition
Missing resources, malformed evidence, or network-dependent loading invalidates
the scenario.

### TD-002 · Deterministic Copilot projection
Requirements: FR-002, FR-003
Type: Unit
Priority: required

#### Purpose
Proves stable native paths, content, and minimal discovery pointer.

#### Scenario
Given identical resolved inputs
When the projection runs twice
Then bundles are equal and canonical references are placed under the Forge
skill.

#### Evidence
Projected artifact paths, contents, and equality assertions.

#### Failure Condition
Reordered or repeated inputs produce different output or the pointer duplicates
canonical workflow content.

### TD-003 · Review-control hook denial
Requirements: FR-004
Type: Unit
Priority: required

#### Purpose
Proves the documented hook denies protected metadata mutations.

#### Scenario
Given a `preToolUse` payload for an Edit or shell mutation of review-control
metadata
When the generated hook runs
Then it returns a deny decision.

#### Evidence
Hook process output parsed as JSON.

#### Failure Condition
The hook allows a protected mutation or emits invalid output.

### TD-004 · Read-only hook allowance
Requirements: FR-004
Type: Unit
Priority: required

#### Purpose
Proves the hook does not block read-only Git inspection of protected paths.

#### Scenario
Given a read-only `git status` payload
When the hook runs
Then it returns allow.

#### Evidence
Hook process output parsed as JSON.

#### Failure Condition
The hook denies a read-only inspection.

### TD-005 · Registry and distribution integration
Requirements: FR-001, FR-005
Type: Integration
Priority: required

#### Purpose
Proves additive registry integration and package visibility without changing
Adapter Core behavior.

#### Scenario
Given the packaged distribution
When registry and distribution tests run
Then the Copilot Adapter is importable and existing adapter tests pass.

#### Evidence
Pytest exit status and distribution assertions.

#### Failure Condition
The Adapter is absent from the package/registry or existing Adapter Core
tests regress.

## Valid RED

The recorded RED failed during collection with the expected missing-package
error before the Adapter existed. It was not a syntax, fixture, or unrelated
infrastructure failure.

## Requirement Coverage

| Requirement | Automated | Manual | Status |
|---|---|---|---|
| FR-001 | TD-001, TD-005 | — | Covered |
| FR-002 | TD-002 | — | Covered |
| FR-003 | TD-002 | — | Covered |
| FR-004 | TD-003, TD-004 | — | Covered |
| FR-005 | TD-005 | — | Covered |

## Coverage Gaps

No mandatory Requirement remains without a verification strategy. Real Copilot
surface execution, Windows CLI hook behavior, IDE agent behavior, and code
review behavior are limitations, not unverified claims of universal coverage.

## Test Design Gate

Every mandatory Requirement has a strategy, critical scenarios identify
observable evidence and failure conditions, automated and Manual Acceptance
are separated, and no Requirement remains without known coverage.
