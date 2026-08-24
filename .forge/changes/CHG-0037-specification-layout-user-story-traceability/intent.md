---
forge:
  artifact: intent
  schema: 1
change: CHG-0037
status: complete
---

# CHG-0037 · Specification Layout User Story Traceability

> **Change Intent**
>
> Evolve the generated Forge Specification into a readable, traceable engineering contract while keeping User Stories optional and Requirements authoritative.

## Overview
| | |
|---|---|
| **Change** | CHG-0037 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

The current Specification scaffold separates Requirements and Acceptance Criteria and has no explicit behavioral-intent layer. This makes it harder for agents and reviewers to follow a need from Discovery through behavior and evidence.

## Goal

Provide a predictable Specification layout with stable User Story, Requirement, Acceptance, and traceability references, without making User Stories or Markdown structure new Gate requirements.

## Scope

Specification guidance, the Change scaffold renderer, related documentation, and tests.

## Out of Scope

No new User Stories artifact, backlog concepts, BDD framework, executable scenario parser, example artifact, Protocol integer, Change Schema, lifecycle command, or automatic end-to-end traceability.

## Success Criteria

New behavioral Changes receive a clear contract layout; technical Changes can omit User Stories; existing historical Specifications and `forge validate` behavior remain valid.
