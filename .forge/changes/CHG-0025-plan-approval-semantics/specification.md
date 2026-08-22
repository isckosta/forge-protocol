---
forge:
  artifact: specification
  schema: 1
change: CHG-0025
status: complete
---

# Specification — Plan Approval Semantics

## Summary

Make the Plan/Implementation authority boundary explicit and mechanically
checkable through the existing human-authority Decision model. Preserve the
existing `status: approved` vocabulary, but require a recorded human Decision
before an active Change may cross `plan_complete`.

## Classification

**FULL.** The change is disqualified from FAST by the authorization-model,
new-domain-invariant, and major-public-contract disqualifiers in
`protocol/flows/fast.yml`. It changes canonical Gate semantics and the
Engineering Contract, requiring RFC, adversarial Specification Review,
Architecture, Test Strategy, and independent Strict Review.

## Functional Requirements

### FR-001 — Explicit Plan authorization

For an active, not-yet-complete Change allocated from CHG-0025 onward whose
Plan is declared `approved`, the manifest MUST contain a material technical Decision with
`owning_artifact: plan`, `authority: human`, `status: resolved`, and
`resolved_via: human_decision`. The Plan and provenance MUST record the
explicit human confirmation and its context.

### FR-002 — Fail closed

Validation MUST report a finding when the required Plan authorization is
absent, unresolved, malformed, or resolved through `autonomous_decision`.
The agent's Recommendation, confidence, or silently self-authored approval
MUST NOT satisfy FR-001. A provenance record observed by `self` is
insufficient; the recorded confirmation MUST identify the operator as
observer. This is recorded repository evidence, not cryptographic or external
attestation.

### FR-003 — Gate dependency

The existing Decision/Gate dependency model MUST treat an asserted approved
Plan as owning the `before_implementation` Gate, so an open material Decision
owned by `plan` blocks that Gate under C-051.

### FR-004 — Existing authority semantics

The implementation MUST reuse the existing `decisions[]` and C-055 authority
vocabulary and the established Plan/provenance approval convention. It MUST
NOT introduce a provider-specific attestation, new CLI command, or
transient-chat-only state.

### FR-005 — Specification Gate distinction

`specification_gate_passed` MUST remain a technical lifecycle Gate. This
Change MUST NOT imply that `specification.md` completion is a human approval,
and MUST NOT require a Plan authorization Decision for that Gate.

### FR-006 — Compatibility boundary

Historical Changes allocated before CHG-0025 MUST remain valid, including
active historical Changes. The new check applies to active Changes allocated
from CHG-0025 onward; the implementation MUST define and test this precise
prospective condition without invalidating the existing Change corpus.

## Acceptance Criteria

- **AC-001:** An active manifest with `artifacts.plan: approved` and no
  matching human Decision produces a validation finding naming Plan
  authorization.
- **AC-002:** The same manifest with an open or autonomously resolved matching
  Decision remains invalid.
- **AC-003:** A matching human-resolved Decision with recorded Plan and
  provenance confirmation passes the new check.
- **AC-004:** A historical manifest allocated before CHG-0025, whether active
  or complete, without the new Decision is not rejected solely by this rule.
- **AC-005:** Existing C-055 Decision behavior and `specification_gate_passed`
  behavior remain unchanged.

## Constraints

- Do not edit `src/forge_cli/app.py`, `src/forge_cli/adapter_cli.py`, any new
  Change command, `src/forge_cli/doctor/__init__.py`, or `examples/`.
- Do not rename the existing `approved` field in this Change.
- Do not claim that Adapter guidance technically enforces human authority.

## Out of Scope

Human approval UX beyond the explicit checkpoint, cryptographic/provider attestations, a new CLI command,
retrofitting completed historical Changes, and extending the requirement to
`specification_gate_passed` without separate evidence of human authority.
