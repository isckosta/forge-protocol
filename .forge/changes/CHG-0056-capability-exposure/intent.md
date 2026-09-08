---
forge:
  artifact: intent
  schema: 1
change: CHG-0056
status: active
---

# CHG-0056 · Capability Exposure

> **Change Intent**
>
> Derive Harness-native discovery and invocation surfaces from Forge's canonical Capability definitions while keeping those definitions Harness-independent.

## Overview
| | |
|---|---|
| **Change** | CHG-0056 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

Forge Capabilities can be loaded by Forge but are not currently projected into native discovery and invocation surfaces. Users cannot reliably discover or explicitly invoke competencies such as `investigate`, and each future Capability would otherwise require bespoke integration work.

## Goal

Provide a reusable, Harness-independent exposure contract and deterministic adapter projections so canonical Capabilities are discoverable and semantically invocable where a Harness officially supports an equivalent surface.

## Scope

This Change covers Capability catalog loading, stable exposure identity, canonical-content projection, supported Harness skill/command discovery, and semantic fallback behavior.

## Out of Scope

It does not add a Protocol slash-command concept, a runtime or executor, lifecycle or governance semantics, unsupported Harness integrations, or root-cause analysis and defect correction behavior.

## Success Criteria

1. Adding a canonical Capability makes it available to compatible Harness adapters without editing the Capability for each Harness.
2. Codex and Claude Code project only officially supported native skill surfaces, with stable names derived from the catalog.
3. The projected skill delegates to the canonical `CAPABILITY.md`, and Harnesses without an equivalent surface remain semantically consumable.
