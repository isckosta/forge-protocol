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
> Publish the merged Forge capability-exposure work as CLI version 0.1.0b4.
> This is a non-behavioral release metadata change; Protocol and runtime behavior are unchanged.

## Overview
| | |
|---|---|
| **Change** | CHG-0057 |
| **Flow** | STANDARD |
| **Status** | Complete |

## Problem

The merged change is available on `main`, but the package metadata and changelog
still identify the previous CLI release.

## Goal

Set the CLI package version to `0.1.0b4` and cut the corresponding changelog
section so the merged behavior can be published through the repository release workflow.

## Scope

This Change covers release metadata and release notes for the already-merged
capability exposure behavior.

## Out of Scope

It does not change Protocol semantics, executable behavior, adapter behavior, or
the canonical Capability definitions.

## Success Criteria

The CLI reports version `0.1.0b4`, the changelog contains the dated release
section, and the release commit is merged through the protected PR workflow.
