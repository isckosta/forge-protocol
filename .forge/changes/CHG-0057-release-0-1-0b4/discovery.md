---
forge:
  artifact: discovery
  schema: 1
change: CHG-0057
status: complete
---

# Discovery — CHG-0057 Release 0 1 0b4

## Executive Summary

The repository release checklist requires a version bump and changelog cut on a
branch, followed by a protected PR merge and tag. `CLI_VERSION` is the single
source of package version truth.

## Investigation

`RELEASING.md` documents PEP 440 progression and the required merged-PR
provenance. The preceding release is `0.1.0b3`; the next evidence-driven
prerelease is `0.1.0b4`.
