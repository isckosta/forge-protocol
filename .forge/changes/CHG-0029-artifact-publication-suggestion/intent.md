---
forge:
  artifact: intent
  schema: 1
change: CHG-0029
status: complete
---

# Intent — CHG-0029 Artifact Publication Suggestion

## Summary

Add a concise, non-binding suggestion to the projected workflow guidance so
that a human can receive the full detail of a completed Strict Review or
Specification without having to discover the repository file manually.

## Problem

The detailed evidence in `review.md` and `specification.md` remains on disk.
The current workflow guidance says how to record it, but does not suggest
offering a Harness-native shareable Artifact when that capability exists.
Claude Code has a documented session-output Artifact capability; Codex's
packaged Adapter exposes no equivalent publication mechanism.

## Desired Outcome

At the end of a key stage, the agent offers to publish the relevant full
Artifact when the active Harness supports shareable Artifacts, while keeping
the repository file authoritative and making no promise for Harnesses without
that capability.

## Scope

- add identical conditional guidance to both Adapter workflow templates;
- mention `review.md` and `specification.md` as candidate Artifacts;
- preserve the existing non-enforcement disclaimer;
- update the remediation roadmap.

## Out of Scope

- no runtime, CLI, Flow, Gate, Contract, schema, or validation change;
- no invented Codex publication mechanism;
- no automatic publication or external upload.

## Success Criteria

- both templates remain byte-identical;
- the guidance is explicitly non-binding and conditional on Harness support;
- the roadmap links the completed CHG-0029;
- targeted schema and repository validation remain clean.
