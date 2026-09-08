---
forge:
  artifact: intent
  schema: 1
change: CHG-0055
status: active
---

# CHG-0055 · 0053 Fix Capability

> **Change Intent**
>
> Define `fix` as a canonical, Harness-independent implementation
> competency that turns a sufficiently understood defect into the smallest
> safe correction with reproducible evidence, while escalating uncertainty
> and material scope expansion.

## Overview
| | |
|---|---|
| **Change** | CHG-0055 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

Forge has a diagnostic `investigate` capability but no complementary
competency for implementing a known repair. Without an explicit boundary,
agents can confuse an inferred cause with an established one, patch a
symptom, or widen a local repair into an architectural or breaking change.

## Goal

1. Define `/fix` for defects whose observed behavior, expected behavior,
   cause, and affected boundary are sufficiently understood.
2. Require a cause-oriented minimal repair, explicit scope protection, and
   proportional regression evidence.
3. Escalate to investigation or human decision when understanding,
   verification, or scope is materially insufficient.

## Scope

The Change covers the canonical Capability Architecture definition of fix,
its applicability, inputs, behavior, outputs, evidence expectations, and
contract-focused tests proving the definition is loadable and bounded.

## Out of Scope

It does not change Flow, TDD, Review, Verification, approval, Merge
Readiness, Protocol, or Engineering Contract semantics; add a mandatory
artifact, execution mode, Gate, registry, executor, or Harness-specific
representation; or implement a product defect.

## Success Criteria

`capabilities/fix/CAPABILITY.md` exists and satisfies the existing contract,
accepts the requested defect inputs, checks sufficient understanding before
implementation, preserves the repair boundary, seeks the smallest
cause-correcting change, detects material scope expansion, and requires
reproducible evidence of restored behavior. It remains usable in any
Forge-enabled repository without changing the existing loader or governance.
