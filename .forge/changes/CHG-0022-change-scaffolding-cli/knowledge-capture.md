---
forge:
  artifact: knowledge_capture
  schema: 1
change: CHG-0022
status: pending
---

# Knowledge Capture — Change Scaffolding CLI

## What Changed

Forge can now create a repository-native Change workspace from the active
canonical Flow.

## Durable Knowledge

Scaffold rendering is pure and publication is exclusive, allowing the CLI to
show the complete plan before mutation and to roll back only content it owns.

## Consequences for Future Changes

Future lifecycle commands can consume the same Flow-derived artifact mapping
and the generated pending manifest instead of duplicating template knowledge.

## References

- `src/forge_cli/change_scaffolding.py`
- `src/forge_cli/change_cli.py`
