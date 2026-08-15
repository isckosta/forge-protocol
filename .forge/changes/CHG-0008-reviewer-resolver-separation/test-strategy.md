---
forge:
  artifact: test_strategy
  schema: 1
change: CHG-0008
status: approved
---

# Test Strategy — Strict Review Iteration 1 Resolution

## TDD cycles

Resolution behavior is test-first. The primary RED commit `d71435f9b2fca5c5829121ff45e0059e67526d84` introduces Protocol 1 compatibility, Protocol 2 provenance, all-Flow enforcement, forged-evidence, revision-binding, shared-boundary, re-review, partial-provenance, and downgrade regressions before production implementation. GitHub Actions run `31900774999`, job `95051092652`, reached the test step and failed while environment/setup succeeded.

A second test-first commit `bb43fae06670e90f5ed07a63f154ec0f541c854d` adds the Adapter version-boundary regression before `CodexProjectionInput` gains Protocol-aware behavior: Protocol 1 must not receive Protocol 2 provenance instructions; Protocol 2 must project them for FAST, STANDARD, and FULL.

## Required adversarial coverage

- Protocol 1 remains valid under pre-CHG-0008 review semantics.
- Protocol 2 passed Review without provenance fails for FAST, STANDARD, and FULL.
- Pairwise-distinct fake identifiers with no provenance record fail.
- Missing/partial provenance fails.
- Provenance bound to the wrong revision fails.
- Shared subject/Reviewer Execution fails.
- Shared subject/Reviewer Context fails.
- Re-review sharing Resolution Context fails.
- Active Protocol 2 `forge/change@1` downgrade fails.
- Completed historical Protocol 1 `forge/change@1` remains valid.
- Independent recorded provenance succeeds for FAST, STANDARD, and FULL.
- Protocol 1 Adapter projection remains free of Protocol 2 semantics.

## GREEN and verification

GREEN requires the complete `pytest -q` suite, then repository `forge validate`, `forge doctor`, and isolated Distribution Verification/wheel/Adapter loading on the final Resolution HEAD. Passing tests are necessary but are not treated as Strict Review acceptance.
