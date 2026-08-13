---
forge:
  artifact: intent
  schema: 1
change: CHG-0001
status: approved
---

# Intent — Bootstrap Forge CLI

## Problem

Forge exists as an engineering Protocol but has no official installation and project-bootstrap mechanism.

Users would otherwise need to construct `.forge/` manually, copy configuration, and determine whether their repository is valid.

## Desired outcome

Provide the first official Forge CLI capable of initializing and validating a Forge-enabled repository.

The CLI remains intentionally limited. It supports Forge infrastructure. It does not execute Forge development workflows.

## Initial commands

- `forge version`
- `forge init`
- `forge validate`
- `forge doctor`

## Success criteria

A developer can install Forge, initialize it in a Git repository, receive valid generated configuration, preserve existing configuration, validate Forge state, diagnose common environment problems, and inspect CLI/Protocol version compatibility.

## Constraints

- Python 3.12+.
- No AI provider dependency.
- No Forge backend.
- No database.
- No development lifecycle execution through the CLI.

## Out of scope

Harness Adapter generation, automatic migration, plugin management, cloud services, LLM execution, dashboards, Specification execution, Review execution, and other normal Change lifecycle actions.
