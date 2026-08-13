---
forge:
  artifact: verification
  schema: 1
change: CHG-0004
status: passed
---

# Verification — Codex Harness Adapter

## Result

Verification passed for CHG-0004 after GitHub review remediation at code commit `5b6a53e5bf98e5bbb4650c20a78fd71bf85ee96d`.

Evidence combines eleven valid TDD cycles, acceptance-invariant tests, generic Core integration tests, isolated-wheel execution with network disabled, packaged Codex resource checks, and runtime dependency audit.

## Final automated suite

- workflow run: `31719038475`;
- job: `94511020787`;
- verified code commit: `5b6a53e5bf98e5bbb4650c20a78fd71bf85ee96d`;
- pytest result: `135 passed`;
- result: SUCCESS.

The final suite includes explicit acceptance checks that repository-native canonical input survives projection generation/discard, Codex projection never requests `shared` ownership, publication-root changes cannot alter projected semantic content/digests, and repeated projection is stable without live vendor input.

## Final isolated distribution and offline operation

- workflow run: `31719038459`;
- job: `94511020449`;
- verified code commit: `5b6a53e5bf98e5bbb4650c20a78fd71bf85ee96d`;
- result: SUCCESS.

The distribution job proves wheel build, wheel-only installation into a clean Python 3.12 environment, installed CLI operation with unreachable HTTP/HTTPS/ALL proxies, packaged generic Adapter schemas, packaged Codex `adapter.yml`, `capabilities.yml`, and workflow skill resource availability, Codex descriptor loading from packaged metadata, deterministic projection generation using packaged workflow framing, generic planning, installation-record construction, generic drift detection, and runtime dependency audit. No OpenAI/Codex SDK dependency is introduced into the generic Core.

Invariant assessment and generic conformance behavior are covered by the automated unit suite. The isolated probe does not claim a Codex-specific conversion into `AdapterRepresentation` followed by `validate_conformance`.

## Acceptance scenarios

- **AC-001 Adapter loads as Codex — PASSED.** TDD-001 proves stable Codex identity, independent version, target Harness, and Protocol interval.
- **AC-002 Skills supported, unverified primitives not claimed — PASSED.** TDD-001 advertises `skills` while leaving hooks, commands, agent roles, and persistent instructions unsupported without evidence.
- **AC-003 Evidence metadata complete — PASSED.** TDD-001/TDD-007 verify capability, status, source, and observation date.
- **AC-004 Deterministic projection bundle — PASSED.** TDD-002 and final acceptance tests prove stable ordered resources for identical canonical input.
- **AC-005 No undocumented publication path — PASSED.** TDD-005 produces no target without explicit or evidence-backed input.
- **AC-006 Gate-preserving projection — PASSED.** TDD-003 preserves Specification Review, RED-before-production, Verification, Strict Review, and Completion semantics represented by the effective Flow.
- **AC-007 Represented but unenforced invariant — PASSED.** TDD-004 classifies textual representation separately from technical enforcement; TDD-010 proves the resulting generic limitation survives planning and installation-record construction even when the representing capability is supported.
- **AC-008 Unsupported capability limitation — PASSED.** TDD-004/TDD-006 retain generic non-enforcement limitations through planning.
- **AC-009 User collision — PASSED.** TDD-006 classifies an existing unowned publication artifact as conflict rather than overwrite.
- **AC-010 Generated drift — PASSED.** TDD-006 reuses generic digest-based drift detection and identifies modified generated artifacts.
- **AC-011 Offline operation — PASSED.** The automated suite covers invariant assessment and generic conformance without live vendor input; Distribution run `31719038459` separately executes the installed Codex descriptor, projection, planning, installation-state, and drift probe with network proxies intentionally unreachable.
- **AC-012 Wheel isolation — PASSED.** Distribution run `31719038459` builds, installs, and probes the wheel outside the source tree.
- **AC-013 Canonical state survives projection deletion — PASSED.** Final acceptance tests prove projection generation/discard does not mutate or replace canonical input; generated artifacts are derived outputs only.
- **AC-014 Evidence does not mutate runtime — PASSED.** TDD-007 packages observation metadata into the release and final acceptance tests prove repeated projection remains identical without live vendor input.

## Functional requirement verification

All 33 Functional Requirements are implemented and verified.

- **FR-001–FR-008:** TDD-001 verifies Adapter identity, independent version, Protocol compatibility, conservative capability declaration, generated-file support, and evidence traceability.
- **FR-009–FR-018:** TDD-002/003/004/005/005B verify canonical-input projection, Codex-only translation boundary, gate preservation, explicit non-enforcement, no capability substitution, and publication independent from undocumented vendor paths.
- **FR-019–FR-024:** TDD-005B/006/010 verify deterministic generic plans, planned-artifact metadata, Forge ownership, user collision protection, absence of Codex `shared` classification, and persistence of capability and invariant limitations as separate planner inputs.
- **FR-025–FR-027:** TDD-004 plus final acceptance tests verify no false compliance, separation of invariant assessment from capability declarations, and canonical semantics winning over publication convention.
- **FR-028–FR-033:** TDD-006/007/010 plus isolated distribution verify local planning, wheel completeness, no Codex SDK dependency in Core, human-reviewable invariant limitations in plans and installation records, generic drift diagnostics, and fixed release evidence/staleness metadata.

## Strict Review remediation

Iteration 1 findings REV-001 and REV-002 were resolved through TDD-008 and TDD-009:

1. `adapter.yml` and `capabilities.yml` are now runtime descriptor/evidence authority rather than duplicated Python constants.
2. `resources/skills/workflow.md` now supplies stable projection framing while stage and Gate content remains derived from canonical Flow input.

Strict Review Iteration 2 passed with no unresolved BLOCKER or MAJOR findings. REV-003 remains an accepted non-blocking test-naming/maintainability risk.

GitHub review reconciliation then exposed REV-005: represented-but-unenforced invariant limitations were created by assessment but could not enter the Codex plan when the representing capability itself was supported. TDD-010 resolved the gap, and Strict Review Iteration 4 passed with no unresolved BLOCKER or MAJOR findings.

Verification status: PASSED.
