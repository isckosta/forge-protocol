---
forge:
  artifact: intent
  schema: 1
change: CHG-0057
status: complete
---

# CHG-0057 · Release 0 1 0b4

> **Change Intent**
>
> Publish the merged capability-exposure work as CLI version 0.1.0b4.
> This is a non-behavioral release metadata change; runtime and Protocol behavior are unchanged.

## Overview
| | |
|---|---|
| **Change** | CHG-0057 |
| **Flow** | STANDARD |
| **Status** | Complete |

## Problem

The merged change is on `main`, but package metadata and release notes still identify the previous CLI release.

## Goal

Set the CLI package version to `0.1.0b4` and cut its changelog section for the protected release workflow.

## Scope

This covers release metadata and notes for already-merged behavior.

## Out of Scope

It does not change executable, Protocol, Capability, or Adapter behavior.

## Success Criteria

The CLI version is `0.1.0b4` and the changelog contains the dated matching section.
