---
forge:
  artifact: discovery
  schema: 1
change: CHG-0054
status: complete
---

# Discovery — CHG-0054 Forge Skill Activation Contract

## Executive Summary

The circular trigger is duplicated in the generated Codex and Claude Code
front matter. Their workflow bodies already carry lifecycle and authority
instructions, so the smallest fix is a routing-only description change plus
cross-Harness tests. No Protocol change is necessary.

## Investigation

The projection builders hard-code the old description and the checked-in
`.agents` and `.claude` files are Forge-owned generated outputs. The Adapter
update path regenerates those outputs and updates their recorded digests. The
activation contract therefore belongs in the projection source and must be
verified for both Harnesses.
