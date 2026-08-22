---
forge:
  artifact: plan
  schema: 1
change: CHG-0025
status: approved
---

# Plan — Plan Approval Semantics

1. Add the C-077 rule to both canonical Contract representations and update
   the artifact guidance to distinguish approved content from human authority.
2. Extend the protocol-version-independent validation path used by Protocol 1
   and Protocol 2 with the active approved-Plan authorization check and include
   approved Plan in the existing Gate dependency model.
3. Add focused regression tests for missing, invalid, valid, and completed
   Plan authorization cases, following the Test Strategy.
4. Update the canonical Flow/projection guidance only where needed to state
   that `plan_complete` requires the recorded Decision; do not touch the
   scaffolding command or prohibited files.
5. Run the focused tests, contract tests, full pytest suite, `forge validate`
   against canonical instances, and documentation consistency checks.
6. Record Verification, TDD evidence, provenance, review, knowledge capture,
   and roadmap completion after the implementation subject is frozen.

## Implementation Boundary

Reaching `plan_complete` is not authorization to begin Implementation. The
human-authority Decision required by C-077 must be recorded before crossing
that boundary. Implementation-time discoveries belong in Verification, a
Decision record, or a documented re-Plan, not in a silent edit to this Plan.

## Explicit approval boundary

This Change adopts the existing repository-native approval convention used by
CHG-0014. The Plan/Implementation boundary requires the user to explicitly
confirm continuation; the confirmation is then recorded here and in
`provenance.yml`. The record is durable repository evidence, not a claim of
cryptographic or provider-native attestation.

**Approval record.** Explicit human approval was received from the user as
“Pode criar” in the active session on 2026-08-22. This confirmation authorizes the
recorded Plan decision and continuation under C-077.
