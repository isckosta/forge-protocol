---
forge:
  artifact: discovery
  schema: 1
change: CHG-0057
status: complete
---

# Discovery — CHG-0057 Release 0 1 0b4

## Executive Summary

`RELEASING.md` requires a PEP 440 version bump, a dated changelog section, a
protected PR merge, and a tag on the merged `main` commit.

## Investigation

`CLI_VERSION` is the single source of package version truth. The preceding
release is `0.1.0b3`; this release is `0.1.0b4`.
