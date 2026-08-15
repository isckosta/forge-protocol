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
- [x] T-022 Add adversarial regressions for all Flows, forged evidence, wrong revision, partial provenance, shared Execution/Context, re-review contamination, and downgrade resistance.
- [x] T-023 Add RED regression preventing Protocol 2 semantics from leaking into Protocol 1 Codex projection.
- [x] T-024 Restore Protocol 1 historical Contract/Specification/Policy/schema semantics.
- [x] T-025 Introduce integer Protocol 2 canonical Specification/Contract/Review Policy resources.
- [x] T-026 Introduce `forge/execution-provenance@1` and Protocol 2 iteration-aware `forge/change@2`.
- [x] T-027 Implement Protocol-aware all-Flow C-026 validation and anti-downgrade behavior.
- [x] T-028 Implement Protocol-aware Contract resolution in validator and Doctor.
- [x] T-029 Make Codex projection Protocol-aware and support Protocols 1–2.
- [x] T-030 Record this Resolution Execution prospectively as `resolution-001` without fabricating historical identifiers.
- [x] T-031 Update canonical and Change documentation/evidence.
- [x] T-032 Confirm final `pytest -q`: 182 passed in 3.83s on `538a77dcd77aed0db0505a288fc1cbea0e69def3`.
- [x] T-033 Confirm isolated `forge validate` and `forge doctor`: PASS in Distribution Verification run `31901397053`.
- [x] T-034 Confirm Distribution Verification, wheel-only installation, Adapter schema/loader probe, and runtime dependency audit: PASS in run `31901397053`.
- [ ] T-035 Obtain independent Strict Re-review Iteration 2 from a Reviewer Execution and Execution Context independent from `resolution-001`.
- [ ] T-036 Complete CHG-0008 only if that independent Reviewer accepts the Resolution and all Completion Gates are satisfied.
