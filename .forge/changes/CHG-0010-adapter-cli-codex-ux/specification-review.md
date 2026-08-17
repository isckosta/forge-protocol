---
forge:
  artifact: specification_review
  schema: 1
change: CHG-0010
status: passed
iteration: 1
---

# Adversarial Specification Review — Adapter CLI and Codex Installation UX

## Review objective

Attempt to reject the proposed public CLI contract for ambiguous mutation
authority, unsafe ownership adoption, incomplete update state transitions,
non-deterministic Codex targeting, or acceptance scenarios that cannot prove
the Roadmap exit criteria.

## Iteration 1 self-review

### SR-001 — Resolved — Configuration ownership was ambiguous

The initial design referred to Adapter configuration without separating it
from Forge-owned installation state. FR-005 now makes `config.yml` user-owned,
explicitly mutable only through `configure`, while FR-019 keeps
`installation.yml` derived and Forge-owned.

### SR-002 — Resolved — Equal bytes could be mistaken for ownership

An unrecorded file equal to desired output could otherwise be adopted during
idempotence handling. FR-014 and INV-002 explicitly prohibit this; AC-004
requires a collision and zero mutation.

### SR-003 — Resolved — Deletion lacked precondition and rollback semantics

The design named obsolete-file cleanup but did not initially bind it to the
prior recorded digest. FR-018 now requires exact recorded ownership proof and
atomic rollback across create, update, delete, and record writes. AC-008 tests
the mixed-operation failure boundary.

### SR-004 — Resolved — “Works from wheel” lacked an end-to-end boundary

FR-024 and AC-001 now require the complete clean-repository onboarding path
from an isolated wheel, while AC-003 through AC-011 exercise safety and recovery
behavior rather than only packaged-resource presence.

## Iteration 1 decision

No blocker or major remains. Human Specification Review confirmed that the 24
functional requirements, five invariants, and twelve acceptance scenarios
accurately bound the approved design. Decision: PASS.
