---
forge:
  artifact: intent
  schema: 1
change: CHG-0036
status: complete
---

# CHG-0036 · Merge Readiness Gate

> **Change Intent**
>
> Establish a repository-native Merge Readiness Gate that determines whether
> the effective revision proposed for integration is authorized by the
> canonical Forge Change evidence. A green generic CI result or a manually
> edited lifecycle claim must not substitute for that determination.

## Overview
| | |
|---|---|
| **Change** | CHG-0036 |
| **Flow** | FULL |
| **Status** | Complete |

## Problem

The repository can currently validate Forge state, record Verification and
Strict Review, and require ordinary CI checks, but it has no single
repository-native decision that combines those facts for the revision about
to enter `main`. This leaves two unsafe gaps: a Change can be valid while
still pending a required lifecycle Gate, and material Forge/runtime/CI
changes can appear in a Pull Request without a governing Change.

## Goal

The Change will make merge authorization mechanically evaluable, locally and
in CI, while preserving the distinction between structural validation and
merge readiness. It will:

1. resolve governing Changes from the effective diff;
2. recompute readiness from canonical Flow requirements and repository-native
   evidence;
3. fail closed on missing, stale, contradictory, or ambiguous evidence; and
4. expose deterministic diagnostics and CI-compatible exit behavior.

## Scope

This Change covers the Forge CLI boundary, a reusable readiness evaluation
engine, Change provenance resolution, evidence admissibility, material-change
policy, CI integration, compatibility treatment for Protocol 1 and 2, and
documentation of the external branch-protection boundary.

## Out of Scope

It does not move lifecycle execution into the CLI, replace Verification or
Strict Review, implement a remote backend, replace GitHub branch protection,
change release provenance, or treat Harness guidance as enforcement.

## Success Criteria

When complete, a revision with no governing Change, stale review subject,
unresolved blocking finding, invalid Resolution chain, stale Plan authority,
incomplete Completion evidence, or unavailable required history cannot receive
a successful Merge Readiness result. A revision governed by one or more
Changes can pass only when every affected Change satisfies its effective Flow.
