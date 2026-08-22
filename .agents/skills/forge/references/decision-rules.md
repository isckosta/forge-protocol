# Forge Decision Structural Rules

Generated directly from the constants `forge validate` enforces (`src/forge_cli/validation/__init__.py`), not hand-maintained prose. If this disagrees with an actual `forge validate` rejection, the code is authoritative and this file is stale.

## Enums

- `class`: architectural, contract, product, technical
- `materiality`: material, non_material
- `status`: analyzing, awaiting_decision, open, resolved, superseded
- `authority`: agent, agent_with_review, human
- `resolved_via`: autonomous_decision, evidence, human_decision (or omit while unresolved)

## `owning_artifact` valid per `class`

- `architectural` -> architecture
- `contract` -> compatibility, specification
- `product` -> specification
- `technical` -> plan, tasks

## Non-negotiable `authority` floor per `class`

- `contract` -> `human`
- `product` -> `human`
