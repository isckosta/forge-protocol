---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0027
status: complete
---
# Knowledge Capture — CHG-0027

- Review cost is not directly measurable from line count. Change footprint,
  semantic impact, Review iterations, finding severity, and recorded span
  are different signals and must not be conflated.
- Historical evidence must use Git objects reachable from the review
  subject. A short SHA from another local branch is not reproducible proof
  for a PR based on `main`.
- A descriptive calibration profile is safer than a numeric score or
  automatic downgrade. Semantic impact and canonical strict Review remain
  authoritative.
- RFC proposal and RFC acceptance are separate lifecycle events. RFC-0005
  is intentionally Proposed and requires a later human acceptance decision.
- Token usage and human attention time are absent from the existing
  provenance records; future calibration must record them before making
  claims about those costs.
