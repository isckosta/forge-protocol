---
forge:
  artifact: intent
  schema: 1
change: CHG-0059
status: active
---

# CHG-0059 · GitHub Copilot Harness Adapter

> **Change Intent**
>
> Add GitHub Copilot as an official Forge Harness Adapter while keeping
> repository-native Forge state authoritative and representing Copilot surface
> limitations explicitly.

## Overview
| | |
|---|---|
| **Change** | CHG-0059 |
| **Flow** | STANDARD |
| **Status** | Active |

## Problem

Forge supports Codex and Claude Code, but GitHub Copilot cannot currently
discover the effective Forge workflow through deterministic repository-native
artifacts. This prevents Forge from projecting its resolved Contract, Flows,
Capabilities, and supported mechanical protections into Copilot without
duplicating canonical state or overstating surface coverage.

## Goal

Provide an installable and diagnosable `github-copilot` Adapter that:

1. projects the effective Forge workflow and canonical Capabilities into
   Copilot-native repository artifacts;
2. preserves Adapter Core ownership, deterministic planning, publication
   safety, drift detection, installation state, and Protocol compatibility;
3. records official capability evidence and explicit surface-dependent
   limitations; and
4. uses Copilot hooks for the review-control protection where the documented
   runtime supports it.

## Scope

The Change covers the packaged Adapter descriptor, publication evidence,
registry integration, deterministic projection of the Forge skill and
Capability skills under `.github/`, the minimal discovery pointer, the
documented Copilot hook projection, tests, and repository documentation.

## Out of Scope

It does not change Forge Protocol semantics, move canonical state into
Copilot-specific files, add separate adapters per Copilot surface, add custom
Reviewer/Resolver agents, add MCP integration, or claim universal enforcement
for surface-dependent Copilot behavior.

## Success Criteria

The packaged `github-copilot` Adapter is discoverable through the existing
registry, produces deterministic offline projections in an arbitrary
Forge-enabled repository, preserves repository authority, and distinguishes
guidance, mechanical enforcement, and unsupported or surface-dependent
guarantees.
