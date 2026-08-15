---
forge:
  artifact: tasks
  schema: 1
change: CHG-0008
status: active
---

# Tasks — Verifiable Review Independence

## Historical implementation and Strict Review

- [x] T-001 Preserve original CHG-0008 TDD and implementation history.
- [x] T-002 Preserve Strict Review Iteration 1 REQUEST CHANGES and findings R001-R004.

## Resolution Iteration 1

- [x] T-020 Record pre-implementation Specification Drift for R001-R004.
- [x] T-021 Add RED regressions for Protocol 1 compatibility and Protocol 2 review provenance.
- [x] T-022 Add RED regressions for FAST/STANDARD/FULL enforcement, forged evidence, wrong revision, partial provenance, shared Execution/Context, re-review contamination, and downgrade resistance.
- [x] T-023 Add RED regression preventing Protocol 2 semantics from leaking into Protocol 1 Codex projection.
- [x] T-024 Restore Protocol 1 Contract, Specification, Review Policy, and `forge/change@1` historical semantics.
- [x] T-025 Introduce integer Protocol 2 canonical Specification/Contract/Review Policy resources.
- [x] T-026 Introduce `forge/execution-provenance@1` and Protocol 2 iteration-aware `forge/change@2`.
- [x] T-027 Implement Protocol-aware C-026 validation and anti-downgrade behavior for FAST/STANDARD/FULL.
- [x] T-028 Implement Protocol-aware Contract resolution in validator and Doctor.
- [x] T-029 Make Codex projection Protocol-aware and support Protocols 1–2.
- [x] T-030 Record this Resolution Execution provenance prospectively as `resolution-001` without fabricating historical identifiers.
- [x] T-031 Update Compatibility, ADR-0008, CHANGELOG, Specification, Architecture, Test Strategy, Plan, Traceability, and Knowledge Capture.
- [ ] T-032 Confirm final `pytest -q` GREEN on Resolution HEAD.
- [ ] T-033 Confirm final `forge validate` and `forge doctor` on Resolution HEAD.
- [ ] T-034 Confirm final Distribution Verification / isolated wheel / Adapter loading on Resolution HEAD.
- [ ] T-035 Obtain independent Strict Re-review Iteration 2 from a Reviewer Execution and Execution Context independent from `resolution-001`.
- [ ] T-036 Complete CHG-0008 only if that independent Reviewer accepts the Resolution and all Completion Gates are satisfied.
