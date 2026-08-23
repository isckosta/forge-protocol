---
forge:
  artifact: architecture
  schema: 1
change: CHG-0027
status: complete
---
# Architecture — Review Cost Proportionality

## Proposed boundary

The RFC deliberately places a future Review Calibration Profile beside
Change planning/review evidence, not inside the canonical semantic
classifier. The classifier continues to select FAST, STANDARD, or FULL
from semantic impact. A profile would describe review emphasis within that
Flow and could never lower a Flow's required stages or canonical Review
policy.

## Proposed information flow

`Change evidence → semantic Flow classification → descriptive calibration
profile → reviewer emphasis/evidence plan → unchanged strict Review`

Candidate dimensions are semantic impact, blast radius, touched
modules/files, additive versus substitutive behavior, external/public
boundary, and test surface. The profile is evidence for a Reviewer, not an
authority that can override Contract or Flow rules.

## Governance and compatibility

The first implementation should be additive and observational. It should
record the declared profile and review outcomes for a bounded pilot, then
revisit calibration after 5–10 Changes. No threshold is proposed as
canonical before that evidence exists. Existing Changes remain valid; no
historical review is reclassified.

## Risks

- Metric gaming: require semantic rationale and Reviewer judgment, not a
  numeric score.
- False reassurance from small diffs: preserve semantic impact, blast
  radius, public boundaries, and strict Review.
- Measurement overhead: start with existing Git, manifest, provenance, and
  review records rather than token telemetry.
- Premature thresholds: require the bounded pilot and explicit acceptance
  before binding rules.
