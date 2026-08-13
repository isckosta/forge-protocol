---
forge:
  artifact: architecture
  schema: 1
change: CHG-0002
status: draft
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

A canonical Adapter manifest describes identity, version, target Harness, supported Protocol range, declared capabilities, and implementation metadata needed for deterministic validation.

Proposed conceptual shape:

```yaml
schema: forge/adapter@1
adapter:
  id: example
  version: 0.1.0
  harness: example-harness
protocol:
  supported: ">=1,<2"
capabilities:
  persistent_instructions: true
  commands: false
  skills: true
  hooks: false
  agent_roles: false
  generated_files: true
```

The exact version-range grammar must be deterministic and documented; CHG-0002 should prefer a deliberately small grammar rather than importing a package-manager semantics accidentally.

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

The planner emits stable operations and limitations.

## Adapter plan

The plan is the reviewable mutation contract.

Conceptual entities:

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

Plan ordering must be deterministic.

## Ownership model

### forge_owned
Created entirely by Forge/Adapter and safe to replace only when current content still matches recorded generated state.

### user_owned
Never silently overwritten.

### shared
May be changed only through an Adapter-defined deterministic merge strategy. Absence of a safe merge strategy produces a conflict.

Ownership is metadata about mutation authority; it does not make Harness artifacts canonical Forge state.

## Installation record

Project-side Adapter state should live under a repository-native namespace such as:

`.forge/adapters/<adapter-id>/installation.yml`

The record stores:

- Adapter identity/version;
- target Harness;
- Protocol compatibility used at install/update time;
- Forge-owned generated artifact paths;
- expected content digests;
- explicit limitations.

It must not duplicate Change lifecycle state.

## Drift model

For Forge-owned artifacts:

```text
expected digest == current digest
    -> safe generated update candidate

expected digest != current digest
    -> externally modified / drifted
    -> conflict, never silent overwrite
```

This is content-based ownership evidence, not merely path-based ownership.

## Capability model

Core owns a stable vocabulary of Forge-relevant capability names. Adapters declare whether each capability is supported.

A missing Harness primitive is not automatically a protocol violation. The critical question is whether the effective Forge invariant can still be faithfully represented. If not, the plan carries an explicit limitation or blocks installation when the invariant is required.

## Conformance boundary

Conformance is evaluated against semantic invariants rather than file names.

Initial checks should include:

- Protocol compatibility;
- no canonical mutation;
- no required Flow-stage omission;
- TDD/RED preservation;
- Strict Review preservation;
- explicit unsupported capabilities;
- no user-owned overwrite;
- repository-native authority preservation.

## Package boundaries

The Python CLI implementation should introduce focused Adapter modules, tentatively:

```text
src/forge_cli/adapters/
    manifest.py
    capabilities.py
    plan.py
    ownership.py
    state.py
    validation.py
```

Harness-specific code does not belong in these modules.

## CLI boundary

CHG-0002 may introduce only infrastructure behavior needed to validate or plan Adapter foundations. It should not add a real Harness Adapter and should not execute SDD lifecycle stages.

## Security

Generated paths must be normalized and confined before mutation. Adapter-provided paths cannot escape the repository/Harness configuration boundary. Symlink and pre-existing-file behavior must be evaluated before Safe Publisher implementation.

## Compatibility

Adapter version, Protocol version, Schema version, and CLI version are independent. The manifest must not imply they advance together.

## Future changes

A first-party Harness Adapter should be a separate Change. That Change will validate whether the Foundation abstraction is sufficient and may propose Protocol refinements through RFC rather than embedding special cases in Core.
