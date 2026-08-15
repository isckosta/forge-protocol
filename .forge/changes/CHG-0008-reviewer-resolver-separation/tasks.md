---
forge:
  artifact: tasks
  schema: 1
change: CHG-0008
status: active
---

# Tasks — Verifiable Review Independence

- [x] T-001 Inspect canonical FULL flow, Review Policy, Change schemas, Contract, Specification, validator, Codex projection, and CHG-0007 structure.
- [x] T-002 Establish initial Reviewer/Resolver separation RED evidence.
- [x] T-003 Introduce `forge/change@2` so mandatory FULL review evidence does not invalidate historical `forge/change@1` Changes.
- [x] T-004 Preserve completed historical Change files without fabricated reviewer evidence.
- [x] T-005 Record Specification Drift from the Laravel stress test showing same-context Role switching can self-review.
- [x] T-006 Define provider-independent Execution and Execution Context as the actual independence boundary.
- [x] T-007 Add test-first regressions for shared context despite distinct executions and shared execution despite distinct context identifiers.
- [x] T-008 Observe valid RED: run `31899409371`, job `95047717053`, `3 failed, 166 passed`.
- [x] T-009 Replace session-shaped reviewer identity with `execution_id`, `context_id`, `resolver_execution_id`, and `resolver_context_id` evidence.
- [x] T-010 Enforce C-026 independently for shared Execution and shared Execution Context.
- [x] T-011 Define Role switching/self-review semantics and independent blocking-finding Resolution/re-review rules in Contract and Specification.
- [x] T-012 Update Review Policy and its schema to require execution-context independence for every Flow.
- [x] T-013 Update Codex projection to project the independent Execution/Context boundary without redefining Core semantics.
- [x] T-014 Update ADR, Architecture, Specification, CHANGELOG, TDD evidence, and Verification for the corrected invariant.
- [x] T-015 Confirm GREEN: Tests run `31899652483`, job `95048292204`, `169 passed`.
- [x] T-016 Confirm Distribution Verification run `31899652482`, job `95048292167` passes from an isolated wheel.
- [ ] T-017 Obtain Strict Review from an Execution and Execution Context independent from this Resolver execution; only that review may create `review.md` and real review identity evidence.
- [ ] T-018 If blocking Findings exist, resolve them outside the Reviewer context and obtain an independent re-review from the Resolution Execution before acceptance.
- [ ] T-019 Complete CHG-0008 only after compliant Review evidence is durably recorded.
