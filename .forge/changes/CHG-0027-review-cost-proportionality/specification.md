---
forge:
  artifact: specification
  schema: 1
change: CHG-0027
status: complete
---
# Specification — Review Cost Proportionality

## Classification

This is a **FULL** Change. The deliverable is prose, but it proposes a
future mechanism affecting canonical Review semantics. FAST is disqualified
by the semantic nature of the proposal: the question is not a localized
copy or validation correction, and its possible consequences reach Review
planning across all Changes. FULL's adversarial Specification Review,
Architecture, Test Strategy, explicit Tasks, and Knowledge Capture are
proportionate safeguards for a proposal that could otherwise weaken
adversarial Review. No automatic downgrade is appropriate.

## Requirements

### FR-001 — Evidence-backed cost dimensions

Discovery and the RFC MUST distinguish Flow classification from review-cost
signals and report real repository-history evidence for at least two
historical Changes, including diff footprint, Review iterations, and any
recorded execution span. Missing token/attention data MUST be disclosed.

### FR-002 — Semantic safeguards

The RFC MUST state that semantic impact remains authoritative and that
diff-only Review, passing tests as sufficient evidence, removal of Strict
Review, and automatic Flow downgrade are not acceptable consequences.

### FR-003 — Concrete bounded proposal

The RFC MUST propose either a concrete calibration mechanism with its
inputs, outputs, pilot boundary, and governance, or a justified decision
not to add one. A line-count-only score is not a sufficient mechanism.

### FR-004 — RFC lifecycle

The Change MUST add RFC-0005 with `Status: Proposed`, cite the real
Proposed/Accepted precedent, and leave acceptance to a later human
decision. The RFC MUST not implement its proposed mechanism.

### FR-005 — Documentation impact

The Change MUST update the remediation status for item #7 to “RFC proposed,
pending human decision” and link this Change. It MUST not modify Flow,
Review policy, Contract, schemas, CLI behavior, or parallel roadmap items.

## Acceptance criteria

- AC-001: historical measurements can be reproduced from cited Git ranges
  and committed manifest/provenance records.
- AC-002: the RFC recommendation has a Confidence rating and limitations.
- AC-003: the proposed profile is descriptive/auditable before it is
  calibrated and does not create an automatic score or downgrade.
- AC-004: the RFC remains Proposed and contains no accepted Contract or
  policy change.
- AC-005: every required non-behavioral artifact records the documentation-
  only nature of this Change honestly.

## Constraints and out of scope

The implementation of a Review Calibration Profile, any new schema field,
Flow/policy/Gate edit, CLI support, token instrumentation, or changes for
items #2–#6 and #8–#10 are explicitly deferred to later, separately
authorized work.
