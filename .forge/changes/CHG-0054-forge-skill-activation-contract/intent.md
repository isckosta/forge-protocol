---
forge:
  artifact: intent
  schema: 1
change: CHG-0054
status: active
---

# CHG-0054 · Forge Skill Activation Contract

> **Change Intent**
>
> Replace the circular Forge skill activation trigger with observable routing
> signals, without turning every repository interaction into a Change.

## Overview
| | |
|---|---|
| **Change** | CHG-0054 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

The description currently asks a Harness to activate Forge only for work it
already knows is a Forge-governed Change. That circular condition can route
material engineering work through another workflow or leave it without Forge
governance.

## Goal

Make material engineering work discoverable before the skill is loaded while
preserving proportional routing:

1. Recognize material behavior implementation/change, material defect fixes,
   existing Change continuation, and explicit Forge requests.
2. Exclude questions, explanations, reading, investigation without a change,
   trivial operations, and immaterial edits from automatic activation.
3. Publish equivalent criteria for compatible Harnesses.

## Scope

The Forge skill activation metadata, its Codex and Claude Code projections,
and automated activation/discovery coverage.

## Out of Scope

Lifecycle rules, Protocol schemas, Harness-specific heuristics, and automatic
activation for every interaction in a Forge-enabled repository.

## Success Criteria

Compatible Harnesses can route clearly material feature and bugfix work,
existing Change continuation, and explicit Forge requests without requiring the
phrase “Forge-governed Change” in advance; non-material and read-only work is
not promoted automatically; and Forge authority remains in the loaded skill.
