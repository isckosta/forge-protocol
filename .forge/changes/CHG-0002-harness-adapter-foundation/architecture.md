---
forge:
  artifact: architecture
  schema: 1
change: CHG-0002
status: approved
---

# Architecture — Harness Adapter Foundation

## Architectural objective

Introduce a Harness Adapter boundary that projects Effective Forge Configuration into Harness-native representation without allowing Harness-specific concerns to redefine canonical Forge semantics.

## Core model

```text
Canonical Protocol
      +
Project Configuration
      +
Project Policies / Contract
      ↓
Effective Forge Configuration
      ↓
Adapter Planner
      ↓
Adapter Plan
      ↓
Safe Publisher
      ↓
Harness-native representation
```

## Adapter manifest

A canonical Adapter manifest describes identity, version, target Harness, explicit Protocol compatibility bounds, and declared capabilities.

```yaml
schema: forge/adapter@1
adapter:
  id: example
  version: 0.1.0
  harness: example-harness
protocol:
  min: 1
  max_exclusive: 2
capabilities:
  persistent_instructions: true
  commands: false
  skills: true
  hooks: false
  agent_roles: false
  generated_files: true
```

Compatibility is exactly `min <= project_protocol < max_exclusive`. Free-form version-range expressions are not part of Protocol v1.

## Adapter planner

Planning is pure with respect to repository mutation.

Conceptual interface:

```python
plan_adapter(
    manifest: AdapterManifest,
    effective_configuration: EffectiveForgeConfiguration,
    repository_state: AdapterRepositoryState,
) -> AdapterPlan
```

The planner emits stable operations, conflicts, and limitations before any mutation.

## Adapter plan

```text
AdapterPlan
├── adapter identity
├── operations[]
├── limitations[]
├── conflicts[]
└── generated-state metadata

AdapterOperation
├── path
├── ownership
├── intent
├── content_digest
└── content?
```

Plan ordering is deterministic.

## Ownership model

### forge_owned
Created entirely by Forge/Adapter and replaceable only when current content still matches recorded expected generated state.

### user_owned
Never silently overwritten.

### shared
May be changed only through an Adapter-defined deterministic merge strategy. No safe merge result means conflict.

Ownership is mutation metadata, never semantic authority.

## Installation record

Project-side Adapter state lives under:

`.forge/adapters/<adapter-id>/installation.yml`

The record contains Adapter identity/version, target Harness, Protocol interval, Forge-owned generated paths and expected digests, and explicit limitations. It must not duplicate Change lifecycle state.

## Drift model

```text
expected digest == current digest
    -> safe generated update candidate

expected digest != current digest
    -> drift/conflict
    -> never silent overwrite
```

Ownership evidence is content-based, not path-only.

## Capability model

Core owns the stable capability vocabulary. Adapter declarations describe Harness primitives.

Forge-required representation needs derive from Effective Forge Configuration and canonical Contract/Flow invariants. Adapter-internal capability needs are separate implementation concerns and cannot redefine Forge requirements.

If a required invariant cannot be faithfully represented, the plan exposes an explicit limitation and must not claim enforcement.

## Conformance boundary

Initial conformance checks cover Protocol compatibility, canonical immutability, required Flow stages/Gates, TDD/RED preservation, Strict Review preservation, explicit limitations, user-owned overwrite protection, and repository-native authority.

## Package boundaries

```text
src/forge_cli/adapters/
    manifest.py
    capabilities.py
    plan.py
    planner.py
    ownership.py
    state.py
    validation.py
    publisher.py
```

Harness-specific implementation does not belong in these modules.

## CLI boundary

CHG-0002 may provide infrastructure needed to validate, plan, install/update, or diagnose Adapter state. It does not add a real Harness Adapter and does not execute SDD lifecycle stages.

## Security

Generated paths are normalized and confined before mutation. Adapter-provided paths cannot escape the intended repository/Harness configuration boundary. Symlink, collision, and pre-existing-file behavior are part of publisher Verification.

## Compatibility

Adapter, Protocol, Schema, and CLI versions are independent.

## Future changes

The first real Harness Adapter is a separate Change. It validates this abstraction against an actual Harness and proposes any necessary Core refinement through RFC rather than special-casing Core.
