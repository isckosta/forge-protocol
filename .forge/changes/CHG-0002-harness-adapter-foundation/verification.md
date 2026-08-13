---
forge:
  artifact: verification
  schema: 1
change: CHG-0002
status: passed
---

# Verification — Harness Adapter Foundation

## Result

Verification passed for the Harness Adapter Foundation after Strict Review remediation at commit `924f7b5ba9a086f5de6744a6426b05ef5c71bb29`.

The evidence combines behavioral tests, isolated-wheel checks, offline execution, Adapter Schema/loader probing, dependency audit, and requirement/acceptance-scenario review.

## V-001 — Invalid Distribution Verification workflow

Severity: MAJOR

Status: RESOLVED

An earlier Distribution Verification workflow failed before job creation because raw Adapter YAML embedded in a Python heredoc broke the GitHub Actions YAML block scalar. Run `31697806566` contained zero jobs and was rejected as Verification evidence.

The workflow was rewritten as valid YAML, the isolated Adapter probe moved to `tests/integration/adapter_wheel_probe.py`, and unreachable proxy constraints were restored. This was a Verification harness defect, not product TDD evidence.

## Final automated suite

- workflow run: `31698601674`;
- job: `94442009987`;
- verified commit: `924f7b5ba9a086f5de6744a6426b05ef5c71bb29`;
- result: SUCCESS;
- pytest result: `93 passed`.

The final suite includes the regression for Strict Review finding REV-001: a `CREATE` target appearing after global preflight must conflict and remain untouched.

## Final isolated distribution and offline operation

- workflow run: `31698601685`;
- job: `94442010635`;
- verified commit: `924f7b5ba9a086f5de6744a6426b05ef5c71bb29`;
- result: SUCCESS.

The distribution job proves wheel build, clean Python 3.12 environment installation, installed CLI execution outside the source tree, `version/init/validate/doctor` with unreachable HTTP/HTTPS/ALL proxies, packaged Adapter Schema resolution, installed manifest and installation-state loader execution under the same offline constraint, and runtime dependency audit.

## Acceptance scenarios

- **AC-001 Compatible Adapter — PASSED.** TDD-002 proves the half-open interval `min <= protocol < max_exclusive`.
- **AC-002 Incompatible Adapter — PASSED.** TDD-002 and TDD-009 reject incompatibility before plan production or mutation.
- **AC-003 Unsupported required invariant — PASSED.** TDD-003 and TDD-008 produce explicit non-enforcement limitations and reject false enforcement.
- **AC-004 User-owned collision — PASSED.** TDD-005/TDD-010 preserve user-owned state; the Strict Review regression additionally closes late CREATE collision replacement.
- **AC-005 Forge-owned deterministic update — PASSED.** TDD-005/007/009/010 require expected generated state and publication preconditions.
- **AC-006 Modified generated artifact — PASSED.** TDD-007/TDD-010 classify divergent generated state as drift/conflict before replacement.
- **AC-007 No semantic authority shift — PASSED.** TDD-006/TDD-008 keep installation state derived and preserve repository semantic authority.
- **AC-008 Deterministic plan — PASSED.** TDD-009 proves stable semantically identical planning for identical inputs.

## Requirement verification

All 35 Functional Requirements are implemented and verified. Non-functional evidence confirms local-first operation, Harness-agnostic Core, deterministic planning, repository-bound publication, and testability without a real Harness SDK.

The isolated-wheel distribution test was added after generic Protocol force-inclusion already packaged the two Adapter Schemas; it therefore started GREEN and is correctly treated as Verification/regression evidence rather than fabricated TDD evidence.

Verification status: PASSED.
