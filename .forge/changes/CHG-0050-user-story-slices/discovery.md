---
forge:
  artifact: discovery
  schema: 1
change: CHG-0050
status: complete
---

# Discovery — CHG-0050 User Story Slices

## Executive Summary

The previous model allowed behavioral Specifications without User Stories and
had no deterministic downstream obligation connecting Stories to work and
Verification.

## Investigation

The existing scaffold exposed optional Story guidance, while traceability was
Requirement-centric. FAST has no Specification stage, so the semantic rule
must remain scoped to Flows that actually produce a Specification. The new
contract therefore uses an explicit observable-behavior marker and exact
repository-native evidence.
