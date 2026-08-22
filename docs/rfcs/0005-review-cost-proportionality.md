# RFC-0005 — Review Cost Proportionality

Status: Proposed

## Summary

This RFC proposes a bounded, descriptive Review Calibration Profile so
Review effort can be planned proportionally within the already-classified
FAST, STANDARD, or FULL Flow. It does not change Flow selection, lower
Strict Review, or make passing tests or diff-only inspection sufficient.

## Motivation

Forge already has a semantic Flow classifier and a strict adversarial Review
policy. The classifier is intentionally not a line-count heuristic, but the
current Protocol has no durable vocabulary for describing review-cost
signals within a selected Flow. The result is that review preparation and
evidence emphasis can be chosen ad hoc.

Repository evidence is suggestive, not a calibrated model. CHG-0021's
28-file, +2,683/-5 Change footprint required 8 TDD cycles and 2 Review
iterations, including a real BLOCKER and a distinct Resolution Verification.
CHG-0020's 17-file, +1,069/-19 footprint required no TDD cycle and 1 Review
iteration; CHG-0024's 11-file, +377/-4 footprint required 1 TDD cycle and
1 Review iteration. These are Change-footprint measurements that include
artifacts. Token usage and human attention time were not recorded.

## Decision proposed

After this RFC is accepted, a separate implementation Change may add an
optional Review Calibration Profile to Change evidence. The first profile
should record these dimensions with a short rationale:

- semantic impact and selected Flow;
- blast radius and touched modules;
- changed-file/diff footprint;
- additive versus substitutive behavior;
- external, public, security, authorization, or persistence boundaries;
- test surface and generated-artifact surface.

The profile produces a reviewer-facing emphasis and evidence plan, not a
numeric approval score. It may say which dimensions deserve deeper
inspection and what evidence must be made easy to find. It must not remove
any required Flow stage, TDD obligation, Verification requirement, Strict
Review, reviewer independence, or documentation impact evaluation.

## Calibration pilot

The implementation should begin observationally for 5–10 Changes. Each
pilot record should preserve the declared dimensions, Review iterations,
finding severities, blocking-resolution occurrences, and any available
wall-clock span. The repository must not infer token cost or human effort
unless it records those measurements directly. Maintainers may propose
thresholds only after reviewing this sample and must make them a separate
Protocol decision.

## Non-goals and safeguards

This RFC does not authorize:

- automatic Flow downgrade from line or file counts;
- a numeric score that can override semantic classification;
- diff-only Review;
- treating passing tests as sufficient;
- removal of adversarial Review or independent reviewer/resolver roles;
- changes to current Flows, Review policy, Contract, schemas, or CLI.

Semantic impact remains authoritative under C-003. The existing
`protocol/policies/review.yml` prohibitions remain authoritative until a
future, separately reviewed Protocol change says otherwise.

## Alternatives rejected

### Lines/files-only automatic depth

Rejected because compact authorization or security changes can have high
semantic impact, while generated or documentation-heavy Changes can have a
large footprint without equivalent risk.

### No additional vocabulary

Rejected as incomplete for the remediation: it leaves review-cost planning
unrecorded and prevents later calibration from repository evidence.

### Immediate mandatory thresholds

Rejected because the repository has only a small, selection-biased sample
and no token or human-attention measurements. A pilot must precede binding
thresholds.

## Compatibility and consequences

The proposal is additive and observational. Existing Change artifacts and
historical Review outcomes remain valid. Acceptance alone does not alter
runtime behavior; a later implementation Change would need to define exact
artifact/schema shape and migration semantics. The likely cost is a small
amount of planning metadata; the benefit is auditable rationale and data
for proportional review calibration.

## Acceptance boundary

This RFC remains **Proposed**. A human maintainer must make a later,
separate acceptance commit, following `docs/rfcs/0002-harness-adapter-
foundation.md` (proposal `f8c8449`, acceptance `bb332ff`) and the same
pattern documented by RFC-0003. This Change must not mark it Accepted or
implement the mechanism it describes.
